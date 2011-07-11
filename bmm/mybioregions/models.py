from django.conf import settings
from django.db import models
from django.contrib.gis.db import models
from django.utils.html import escape
from lingcod.features.models import PolygonFeature, FeatureCollection
from lingcod.analysistools.models import Analysis
from lingcod.features import register, alternate
from lingcod.common.utils import asKml
from lingcod.unit_converter.models import area_in_display_units
import os
import time
import math

BIOREGION_SIZES = ( # in millions of Hectares
    (4, 'Very Small'),
    (20, 'Small'),
    (50, 'Medium'),
    (100, 'Large'),
    (250, 'Very Large'),
)

@register
class MyBioregion(Analysis):
    
    #Input Parameters
    #input_start_point = models.TextField(verbose_name='Population Center')
    input_starting_point = models.PointField(srid=settings.GEOMETRY_CLIENT_SRID, null=True, blank=True, verbose_name="Bioregion Starting Point")
    input_temp_weight = models.FloatField(verbose_name='Value given to Temperature')
    input_language_weight = models.FloatField(verbose_name='Value given to Spoken Language')
    input_precip_weight = models.FloatField(verbose_name='Value given to Precipitation')
    input_biomass_weight = models.FloatField(verbose_name='Value given to Vegetation')
    input_bioregion_size = models.FloatField(choices=BIOREGION_SIZES, 
            verbose_name='Relative size of Bioregion', default=50)
    
    #Descriptors (name field is inherited from Analysis)
    description = models.TextField(null=True, blank=True)
    
    # All output fields should be allowed to be Null/Blank
    output_geom = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Bioregion Geometry")
    
    def run(self):
        from lingcod.analysistools.grass import Grass

        coords = self.input_starting_point.transform(settings.GEOMETRY_DB_SRID, clone=True)
        p_temp = self.input_temp_weight
        p_precip = self.input_precip_weight
        p_language = self.input_language_weight
        p_biomass = self.input_biomass_weight

        g = Grass('world_moll', 
                gisbase="/usr/local/grass-6.4.1RC2", 
                gisdbase="/home/grass",
                autoclean=True)
        g.verbose = False
        rasts = g.list()['rast']

        outdir = '/tmp'
        outbase = 'bioregion_%s' % str(time.time()).split('.')[0]
        output = os.path.join(outdir,outbase+'.json')
        if os.path.exists(output):
            raise Exception(output + " already exists")


        # Guess seed value
        x = (p_temp + p_language + p_precip + p_biomass + 0.5) 
        t_weight = ((14.7965 * x ) ** 0.7146) 
        const1 = 20000
        max_cost = x * const1 / t_weight

        desired_size_mHa = self.input_bioregion_size #million Hectares
        desired_size = 10000000000 * desired_size_mHa
        radius = math.sqrt(desired_size/math.pi) 
        buff = coords.buffer(radius*3) # x3 to be safe against long skinny bioregions

        # set initial region
        g.run('g.region rast=soilmoist')
        print 'g.region w=%d s=%d e=%d n=%d' % buff.extent 
        g.run('g.region w=%d s=%d e=%d n=%d' % buff.extent )
        g.run('r.mapcalc "weighted_combined_slope = 0.5 + ' +
                            '(%s * temp_slope)*100 + ' % p_temp  + 
                            '(%s * lang_slope)*100 + ' % p_language +
                            '(%s * precip_slope)*100 + ' % p_precip +
                            '(%s * biomass_slope)*100' % p_biomass +
                            '"')

        ################# Run #2 - adjusted cost #####################
        tolerance = 0.1
        ratio = 0.0
        seed_low = True
        seed_high = True
        seed = True
        i = 0
        largest_area = desired_size
        overs = []
        unders = []
        while ratio < (1-tolerance) or ratio > (1+tolerance):
            g.run('g.region n=7078485 s=3660936 e=-7024061 w=-10560592')
            g.run('r.cost -k input=weighted_combined_slope output=cost1 coordinate=%s,%s max_cost=%s' % \
                    (coords[0],coords[1],max_cost) )
            g.run('r.mapcalc "bioregion1=if(cost1 >= 0)"')
            g.run('r.to.vect input=bioregion1 output=bioregion1_poly feature=area') # -s
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

            print "* run %s ratio %s max_cost %s actual_size %s desired_size %s" % (i, 
                    ratio,
                    max_cost, 
                    int((largest_area/10000.0)/1000000.0),  
                    int((desired_size/10000.0)/1000000.0))

            try:
                # take the average of the highest underestimate and the lowest overestimate
                max_cost = (max(unders) + min(overs))/2.0
            except ValueError:
                max_cost = max_cost * (ratio ** 0.5)

            if seed and ratio < 0.15 and seed_low: 
                # we are WAY overestimating max_cost, try a very low cost 
                seed_low = False
                max_cost = max_cost / 5.0
                print "Seeding low"

            if seed and ratio > 20 and seed_high: 
                # we are WAY underestimating max_cost, try a very high cost 
                seed_high = False
                max_cost = max_cost * 10.0
                print "Seeding high"

            # avoid getting stuck if tolerance is too tight
            if delta_area == 0 and ratio > (1-tolerance*2) and ratio < (1+tolerance*2) :
                tolerance = tolerance * 2

            i = i+1
            # If we haven't gotten it by 25 iterations, just call it good 
            if i>25:
                break


        geom.srid = settings.GEOMETRY_DB_SRID 
        g2 = geom.buffer(-17000) # rougly 2x cellsize
        geom = g2.buffer(17000)
        if geom and not settings.DEBUG:
            os.remove(output)
            del g
        self.output_geom = geom
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
