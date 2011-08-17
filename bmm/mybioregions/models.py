from django.conf import settings
from django.db import models
from django.contrib.gis.db import models
from django.utils.html import escape
from lingcod.features.models import PolygonFeature, FeatureCollection
from lingcod.analysistools.models import Analysis
from lingcod.features import register, alternate
from lingcod.common.utils import asKml, get_logger
from lingcod.unit_converter.models import area_in_display_units
import os
import time
import math

logger = get_logger()

BIOREGION_SIZES = (
    ('VS', 'Very Small (2m Hectares)'),
    ('S', 'Small (5m Hectares)'),
    ('M', 'Medium (20m Hectares)'),
    ('L', 'Large (50m Hectares)'),
    ('VL', 'Very Large (100m Hectares)'),
)

SIZE_LOOKUP = { # in millions of Hectares
    'VS': 2, 
    'S': 5, 
    'M': 20,
    'L': 50,
    'VL': 100
}

try:
    REMOVE_MAPSET_AFTER_RUN = settings.REMOVE_MAPSET_AFTER_RUN
except:
    REMOVE_MAPSET_AFTER_RUN = True

@register
class MyBioregion(Analysis):
    
    #Input Parameters
    input_starting_point = models.PointField(srid=settings.GEOMETRY_CLIENT_SRID, null=True, 
            blank=True, verbose_name="Bioregion Starting Point")
    input_temp_weight = models.FloatField(verbose_name='Value given to Temperature')
    input_precip_weight = models.FloatField(verbose_name='Value given to Precipitation')
    input_biomass_weight = models.FloatField(verbose_name='Value given to Vegetation')
    input_lang_weight = models.FloatField(verbose_name='Value given to Language')
    input_elev_weight = models.FloatField(verbose_name='Value given to Elevation')
    input_marine_weight = models.FloatField(verbose_name='Value given to Marine Environment')
    input_bioregion_size = models.CharField(choices=BIOREGION_SIZES, max_length=3,
            verbose_name='Relative size of Bioregion', default='S')
    
    #Descriptors (name field is inherited from Analysis)
    description = models.TextField(null=True, blank=True)
    satisfied = models.BooleanField(default=False)
    
    # All output fields should be allowed to be Null/Blank
    output_geom = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Bioregion Geometry")
    output_numruns = models.IntegerField(null=True, blank=True)
    output_initcost = models.FloatField(null=True, blank=True)
    output_finalcost = models.FloatField(null=True, blank=True)

    
    def run(self):
        from lingcod.analysistools.grass import Grass

        coords = self.input_starting_point.transform(settings.GEOMETRY_DB_SRID, clone=True)
        p_temp = self.input_temp_weight
        p_precip = self.input_precip_weight
        p_biomass = self.input_biomass_weight
        p_lang = self.input_lang_weight
        p_elev = self.input_elev_weight
        p_marine = self.input_marine_weight

        g = Grass(settings.GRASS_LOCATION,
                gisbase=settings.GRASS_GISBASE,
                gisdbase=settings.GRASS_GISDBASE,
                autoclean=REMOVE_MAPSET_AFTER_RUN)
        g.verbose = not REMOVE_MAPSET_AFTER_RUN # go verbose only if we're not removing the mapset
        rasts = g.list()['rast']

        outdir = '/tmp'
        outbase = 'bioregion_%s' % str(time.time()).split('.')[0]
        output = os.path.join(outdir,outbase+'.json')
        if os.path.exists(output):
            raise Exception(output + " already exists")

        # Guess seed value
        desired_size_mHa = SIZE_LOOKUP[self.input_bioregion_size] #million Hectares
        desired_size = 10000000000 * desired_size_mHa
        radius = math.sqrt(desired_size/math.pi) 
        buff = coords.buffer(radius*5) # to be safe against long skinny bioregions

        x = p_temp + p_precip + p_biomass + p_lang + p_elev + p_marine 
        dist_constant = 0.0
        # TODO
        # regression, R^2 ~ 0.38 for 275 random samples
        intercept = 0 #464070
        max_cost = math.fabs((3162 * x * (desired_size_mHa ** 0.5))+intercept)

        self.output_initcost = max_cost
        if x - p_marine < 1:
            dist_constant = 2.0

        # set initial region
        g.run('g.region rast=biomass_slope')
        g.run('g.region w=%d s=%d e=%d n=%d' % buff.extent )
        start_values = get_raster_values(g, rasts, coords)
        start_values['ocean_slope'] = get_nearest_ocean_value(g, coords)
        
        g.run('r.mapcalc "weighted_land_slope = %s + ' % dist_constant +
                            '(%s * pow(abs(%s - temp_slope),2))*10 + ' % (p_temp,start_values['temp_slope'])  + 
                            '(%s * pow(abs(%s - precip_slope),2))*10 + ' % (p_precip,start_values['precip_slope'])  + 
                            '(%s * pow(abs(%s - biomass_slope),2))*10 + ' % (p_biomass,start_values['biomass_slope'])  + 
                            '(%s * pow(abs(%s - lang_slope),2))*10 + ' % (p_lang,start_values['lang_slope'])  + 
                            '(%s * pow(abs(%s - elev_slope),2))*10' % (p_elev,start_values['elev_slope'])  + 
                            '"')

        if p_marine >= 1:
            '''
            We need a distance constant to prevent 'runout' - this needs to be inversely propotional to the marine weighting
            For the multiplier, normalize to other layers (10^5 = 1000000 then divide by the marine weight)
            '''
            g.run('r.mapcalc "weighted_ocean_slope = (10000000/%s) + ' % (p_marine,) + 
                            '(%s * pow(abs(%s - ocean_slope),2))*(1000000/%s)' % (p_marine,start_values['ocean_slope'], p_marine )  + 
                            '"')
            g.run('r.mapcalc "weighted_combined_slope = if(isnull(weighted_ocean_slope),0,weighted_ocean_slope) + ' + 
                  'if(isnull(weighted_land_slope),0,weighted_land_slope)"')
        else:
            # Don't include the ocean at all, just use the land slope
            g.run('g.rename rast=weighted_land_slope,weighted_combined_slope')

        # iterate over cost_distance analysis until we converge on a reasonable size
        tolerance = 0.15
        ratio = 0.0
        i = 0
        delta_zero_count = 0
        largest_area = desired_size
        overs = []
        overs_sizes = []
        unders = []
        unders_sizes = []
        while True:
            g.run('g.region w=%d s=%d e=%d n=%d' % buff.extent )
            g.run('r.cost -k input=weighted_combined_slope output=cost1 coordinate=%s,%s max_cost=%s' % \
                    (coords[0],coords[1],max_cost) )
            g.run('r.mapcalc "bioregion1=if(cost1 >= 0)"')
            g.run('r.to.vect -s input=bioregion1 output=bioregion1_poly feature=area') 
            if os.path.exists(output):
                os.remove(output)
            g.run('v.out.ogr -c input=bioregion1_poly type=area format=GeoJSON dsn=%s' % output)
            old_area = largest_area
            largest_area, geom = get_largest_from_json(output)
            delta_area = largest_area - old_area

            ratio = desired_size/largest_area
            logger.debug("#%s ratio %s max_cost %s actual %s desired %s" % (i, 
                    ratio,
                    max_cost, 
                    int((largest_area/10000.0)/1000000.0),  
                    int((desired_size/10000.0)/1000000.0)))
            if ratio > (1-tolerance) and ratio < (1+tolerance):
                break 

            if ratio < 1.0 : 
                overs.append(max_cost)
                overs_sizes.append(largest_area)
            else:
                unders.append(max_cost)
                unders_sizes.append(largest_area)


            try:
                #estimate the placement between
                #highest underestimate and the lowest overestimate
                usd = desired_size - max(unders_sizes)
                osd = min(overs_sizes) - desired_size
                tsd = float(usd + osd)
                max_cost = max(unders) * osd/tsd + min(overs) * usd/tsd
                #simple average method 
                #avgc = (max(unders) + min(overs))/2.0
                #logger.debug("Estimating between high and low... %s (or %s using simple average)" % (max_cost, avgc))
            except ValueError:
                max_cost = max_cost * (ratio ** 0.67)

            if ratio < 0.99 and len(unders)==0: 
                # we are overestimating max_cost, try a very low cost 
                try:
                    max_cost = min(overs) / 10.0
                except:
                    max_cost = max_cost / 10.0

            if ratio > 1.01 and len(overs)==0: 
                # we are underestimating max_cost, try a very high cost 
                try:
                    max_cost = max(unders) * 10.0
                except:
                    max_cost = max_cost * 10.0

            # avoid getting stuck if tolerance is too tight
            if delta_area == 0:
                delta_zero_count += 1
            else:
                delta_zero_count = 0
            if i>16 or delta_zero_count > 3:
                break
            if delta_zero_count > 1 and (ratio > (1-tolerance*2) or ratio < (1+tolerance*2)) :
                tolerance = tolerance * 1.25
                logger.debug("Expanding tolerance to %s " % tolerance)
                continue

            i += 1

        geom.srid = settings.GEOMETRY_DB_SRID 
        if geom and REMOVE_MAPSET_AFTER_RUN: 
            os.remove(output)
            del g

        if not geom.valid:
            geom = geom.buffer(0)
            
        if geom.valid:
            self.output_geom = geom
            self.output_numruns = i
            self.output_finalcost = max_cost
        else:
            logger.debug("%s is not a valid geometry!" % self.name)
            
        # New shape, have user confirm it
        self.satisfied = False
        return True
        
    def save(self, *args, **kwargs):
        if 'rerun' in kwargs.keys():
            rerun = kwargs['rerun']
            del kwargs['rerun']
        else:
            rerun = False
            # only rerun the analysis if any of the input_ fields have changed
            # ie if name and description change no need to rerun the full analysis
            if self.pk is None:
                rerun = True
            else:
                orig = MyBioregion.objects.get(pk=self.pk)
                for f in MyBioregion.input_fields():
                    # Is original value different from form value?
                    if orig._get_FIELD_display(f) != self._get_FIELD_display(f):
                        rerun = True
                        break
        super(MyBioregion, self).save(rerun=rerun)

    @classmethod
    def mapnik_geomfield(self):
        return "output_geom"

    @classmethod
    def mapnik_style(self):
        import mapnik
        polygon_style = mapnik.Style()
        ps = mapnik.PolygonSymbolizer(mapnik.Color('#551A8B'))
        ps.fill_opacity = 0.9
        ls = mapnik.LineSymbolizer(mapnik.Color('#ffffff'),0.75)
        ls.stroke_opacity = 0.9
        ts = mapnik.TextSymbolizer('name','DejaVu Sans Bold',11,mapnik.Color('#555555'))
        ts.displacement(15,15)
        ts.halo_fill = mapnik.Color('white')
        ts.halo_radius = 1
        ts.opacity = 0.5
        r = mapnik.Rule()
        r.symbols.append(ps)
        r.symbols.append(ls)
        r.symbols.append(ts)
        polygon_style.rules.append(r)
        return polygon_style

    @property 
    def kml_working(self):
        return """
        <Placemark id="%s">
            <visibility>0</visibility>
            <name>%s (WORKING)</name>
        </Placemark>
        """ % (self.uid, escape(self.name))

    @property
    def done(self):
        # For now just check that the geom is complete 
        if self.output_geom is None:
            return False
        return True

    @property 
    def kml_done(self):
        return """
        %s
        <Placemark id="%s">
            <visibility>1</visibility>
            <name>%s</name>
            <styleUrl>#%s-default</styleUrl>
            <MultiGeometry>
            %s
            %s
            </MultiGeometry>
        </Placemark>
        """ % (self.kml_style, self.uid, escape(self.name), self.model_uid(),
            asKml(self.output_geom.transform(
                    settings.GEOMETRY_CLIENT_SRID, clone=True),uid=self.uid),
            asKml(self.input_starting_point.transform(
                    settings.GEOMETRY_CLIENT_SRID, clone=True),uid=self.uid))
    
    @property
    def kml_style(self):
        return """
        <Style id="%s-default">
            <IconStyle>
                <color>ffffffff</color>
                <colorMode>normal</colorMode>
                <scale>0.9</scale> 
                <Icon> <href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href> </Icon>
            </IconStyle>
            <LabelStyle>
                <color>ffffffff</color>
                <scale>0.8</scale>
            </LabelStyle>
            <PolyStyle>
                <color>778B1A55</color>
            </PolyStyle>
        </Style>
        """ % (self.model_uid(),)
    
    @property
    def hash(self):
        """"
        We are only concerned with the geometry here
        """
        geom_wkt = "%s" % (self.output_geom.wkt)
        return geom_wkt.__hash__()        
        
    def convert_to_shp(self):
        '''
        Port the Bioregion attributes over to the BioregionShapefile model so we can export the shapefile.
        '''
        bsf, created = BioregionShapefile.objects.get_or_create(bioregion=self)
        if created or bsf.date_modified < self.date_modified:
            bsf.name = self.name
            bsf.bio_id_num = self.pk
            bsf.geometry = self.output_geom
            #short_name = self.name
            if self.collection:
                bsf.group = self.collection
                bsf.group_name = self.collection.name
            #units based on the settings variable DISPLAY_AREA_UNITS (currently sq miles)
            bsf.area_sq_mi = area_in_display_units(self.output_geom)
            bsf.author = self.user.username
            bsf.bio_modification_date = self.date_modified
            bsf.save()
        return bsf
    
    class Options:
        verbose_name = 'Bioregion'
        icon_url = 'bmm/img/regions.png'
        form = 'mybioregions.forms.MyBioregionForm'
        form_template = 'mybioregion/form.html'
        show_template = 'mybioregion/show.html'
        links = (
            alternate('Shapefile',
                'mybioregions.views.bmm_shapefile',
                select='multiple single',
                type='application/zip',
            ),
        )

@register
class Folder(FeatureCollection):
    #name field is inherited from FeatureCollection
    description = models.TextField(null=True, blank=True)
    
    class Options:
        form = 'mybioregions.forms.FolderForm'
        #form_template = 'folder/form.html'
        show_template = 'folder/show.html'
        valid_children = (
            'bmm.mybioregions.models.MyBioregion',
            'bmm.mybioregions.models.Folder',
            'bmm.mybioregions.models.Placeholder',
        )
        links = (
            alternate('Shapefile',
                'mybioregions.views.bmm_shapefile',
                select='multiple single',
                type='application/zip',
            ),
        )
       
class Placeholder(PolygonFeature):
    description = models.TextField(default="", null=True, blank=True)

    class Options:
        manipulators = []
        verbose_name = 'Bioregion Placeholder'
        form = 'mybioregions.forms.PlaceholderForm'
        show_template = 'placeholder/show.html'
      
class BioregionShapefile(models.Model):
    """
    This model will provide the correct fields for the export of shapefiles using the django-shapes app.
    """
    geometry = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,blank=True,null=True)
    name = models.CharField(max_length=255)
    bio_id_num = models.IntegerField(blank=True, null=True)
    group = models.ForeignKey(Folder, null=True, blank=True)
    group_name = models.CharField(blank=True, max_length=255, null=True)
    area_sq_mi = models.FloatField(blank=True,null=True)
    author = models.CharField(blank=True, max_length=255,null=True)
    bioregion = models.OneToOneField(MyBioregion, related_name="bioregion")
    bio_modification_date = models.DateTimeField(blank=True, null=True)
    date_modified = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    objects = models.GeoManager()      

def get_largest_from_json(output):
    from django.contrib.gis.gdal import DataSource
    ds = DataSource(output)
    layer = ds[0]
    geom = layer[0].geom.geos

    # Take the single polygon with the largest geometry 
    # Assume the rest are slivers, etc
    largest_area = geom.area
    for feat in layer[1:]:
        if feat.geom.area > largest_area:
            largest_area = feat.geom.area
            geom = feat.geom.geos
    return largest_area, geom

def get_raster_values(g, rasts, coords):
    what = g.run('r.what input=%s east_north=%s,%s' % (','.join(rasts), coords[0], coords[1]))
    startvals = {}
    vals = what.strip().split('|')[3:]
    assert len(vals) == len(rasts)
    for i in range(len(vals)):
        val = vals[i]
        rast = rasts[i]
        try:
            realval = float(val)
        except:
            realval = 0
        startvals[rast] = realval
    return startvals

def get_nearest_ocean_value(g, coords):
    g.run('echo "%s|%s|1" | v.in.ascii output=start_pnt' % (coords[0],coords[1]))
    g.run('v.to.rast type=point use=cat input=start_pnt output=start_rast')
    output = g.run('r.distance maps=start_rast,ocean_slope fs=","')
    min_dist = 999999999
    ocean_val = None
    lines = output.strip().split("\n")
    for line in lines:
        d = line.strip().split(",")
        try:
            dist = float(d[2])
            #coords = (d[5],d[6])
            if dist < min_dist:
                min_dist = dist
                ocean_val = float(d[1])
        except:
            pass
    if ocean_val is None:
        ocean_val = 1.0
    return ocean_val

