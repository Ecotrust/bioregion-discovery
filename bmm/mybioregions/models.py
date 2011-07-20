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
    ('VS', 'Very Small'),
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
    ('VL', 'Very Large'),
)

SIZE_LOOKUP = { # in millions of Hectares
    'VS': 2, 
    'S': 5, 
    'M': 20,
    'L': 50,
    'VL': 100
}
SAVE_MAPSET = False

@register
class MyBioregion(Analysis):
    
    #Input Parameters
    #input_start_point = models.TextField(verbose_name='Population Center')
    input_starting_point = models.PointField(srid=settings.GEOMETRY_CLIENT_SRID, null=True, blank=True, verbose_name="Bioregion Starting Point")
    input_temp_weight = models.FloatField(verbose_name='Value given to Temperature')
    input_precip_weight = models.FloatField(verbose_name='Value given to Precipitation')
    input_biomass_weight = models.FloatField(verbose_name='Value given to Vegetation')
    input_bioregion_size = models.CharField(choices=BIOREGION_SIZES, max_length=3,
            verbose_name='Relative size of Bioregion', default='M')
    
    #Descriptors (name field is inherited from Analysis)
    description = models.TextField(null=True, blank=True)
    
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

        g = Grass(settings.GRASS_LOCATION,
                gisbase=settings.GRASS_GISBASE,
                gisdbase=settings.GRASS_GISDBASE,
                autoclean=True)
        g.verbose = False
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

        x = p_temp + p_precip + p_biomass 
        dist_constant = 0.0
        # regression, R^2 ~ 0.43 for 250 random samples
        max_cost = math.fabs((4283 * x * (desired_size_mHa ** 0.5))+122119)

        self.output_initcost = max_cost
        if x < 1:
            dist_constant = 2.0


        # set initial region
        g.run('g.region rast=biomass_slope')
        g.run('g.region w=%d s=%d e=%d n=%d' % buff.extent )
        #rasts = ['biomass_slope','temp_slope','precip_slope']
        start_values = get_raster_values(g, rasts, coords)
        start_values['ocean_slope'] = get_nearest_ocean_value(g, coords)
        
        g.run('r.mapcalc "weighted_combined_slope = %s + ' % dist_constant +
                            #'(%d * ocean_mask) +' % 10.0**12 +
                            '(%s * pow(abs(%s - temp_slope),2))*10 + ' % (p_temp,start_values['temp_slope'])  + 
                            '(%s * pow(abs(%s - precip_slope),2))*10 + ' % (p_precip,start_values['precip_slope'])  + 
                            '(%s * pow(abs(%s - biomass_slope),2))*10' % (p_biomass,start_values['biomass_slope'])  + 
                            '"')

        ################# Run #2 - adjusted cost #####################
        tolerance = 0.15
        ratio = 0.0
        seed_low = True
        seed_high = True
        seed = True
        i = 0
        delta_zero_count = 0
        largest_area = desired_size
        overs = []
        unders = []
        while ratio < (1-tolerance) or ratio > (1+tolerance):
            g.run('g.region w=%d s=%d e=%d n=%d' % buff.extent )
            g.run('r.cost -k input=weighted_combined_slope output=cost1 coordinate=%s,%s max_cost=%s' % \
                    (coords[0],coords[1],max_cost) )
            g.run('r.mapcalc "bioregion1=if(cost1 >= 0)"')
            g.run('r.to.vect -s input=bioregion1 output=bioregion1_poly feature=area') # -s
            if os.path.exists(output):
                os.remove(output)
            g.run('v.out.ogr -c input=bioregion1_poly type=area format=GeoJSON dsn=%s' % output)
            old_area = largest_area
            largest_area, geom = get_largest_from_json(output)
            delta_area = largest_area - old_area

            ratio = desired_size/largest_area
            if ratio < 1.0 : 
                overs.append(max_cost)
            else:
                unders.append(max_cost)

            logger.debug("* run %s ratio %s max_cost %s actual_size %s desired_size %s" % (i, 
                    ratio,
                    max_cost, 
                    int((largest_area/10000.0)/1000000.0),  
                    int((desired_size/10000.0)/1000000.0)))

            try:
                # always try to take the average of the 
                # highest underestimate and the lowest overestimate
                max_cost = (max(unders) + min(overs))/2.0
            except ValueError:
                max_cost = max_cost * (ratio ** 0.67)

            if seed and ratio < 0.15 and seed_low: 
                # we are WAY overestimating max_cost, try a very low cost 
                seed_low = False
                max_cost = max_cost / 5.0
                logger.debug("Seeding low")

            if seed and ratio > 20 and seed_high: 
                # we are WAY underestimating max_cost, try a very high cost 
                seed_high = False
                max_cost = max_cost * 5.0
                logger.debug("Seeding high")

            # avoid getting stuck if tolerance is too tight
            if delta_area == 0:
                delta_zero_count += 1
            else:
                delta_zero_count = 0

            if delta_zero_count > 2 and (ratio > (1-tolerance*2) or ratio < (1+tolerance*2)) :
                tolerance = tolerance * 1.25
                logger.debug("Expanding tolerance to %s " % tolerance)
                continue

            i += 1
            if i>16 or delta_zero_count > 4:
                break


        geom.srid = settings.GEOMETRY_DB_SRID 
        if geom and not SAVE_MAPSET: 
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
        ps = mapnik.PolygonSymbolizer(mapnik.Color('#ffffff'))
        ps.fill_opacity = 0.5
        ls = mapnik.LineSymbolizer(mapnik.Color('#555555'),0.75)
        ls.stroke_opacity = 0.5
        r = mapnik.Rule()
        r.symbols.append(ps)
        r.symbols.append(ls)
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
                    settings.GEOMETRY_CLIENT_SRID, clone=True)),
            asKml(self.input_starting_point.transform(
                    settings.GEOMETRY_CLIENT_SRID, clone=True)))
    
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

