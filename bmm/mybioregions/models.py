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


@register
class MyBioregion(Analysis):
    
    #Input Parameters
    #input_start_point = models.TextField(verbose_name='Population Center')
    input_starting_point = models.PointField(srid=settings.GEOMETRY_CLIENT_SRID, null=True, blank=True, verbose_name="Bioregion Starting Point")
    input_temp_weight = models.FloatField(verbose_name='Value given to Temperature')
    input_language_weight = models.FloatField(verbose_name='Value given to Spoken Language')
    input_precip_weight = models.FloatField(verbose_name='Value given to Precipitation')
    input_biomass_weight = models.FloatField(verbose_name='Value given to Vegetation')
    
    #Descriptors (name field is inherited from Analysis)
    description = models.TextField(null=True, blank=True)
    
    # All output fields should be allowed to be Null/Blank
    output_geom = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Bioregion Geometry")
    
    def run(self):
        from lingcod.analysistools.grass import Grass

        coords = self.input_starting_point.transform(settings.GEOMETRY_DB_SRID, clone=True)
        max_cost=100 * (self.input_temp_weight + self.input_language_weight + \
                        self.input_precip_weight + self.input_biomass_weight)

        g = Grass('world_moll', 
                gisbase="/usr/local/grass-6.4.1RC2", 
                gisdbase="/home/grass",
                autoclean=True)
        g.verbose = True
        g.run('g.region rast=soilmoist')
        rasts = g.list()['rast']

        outdir = '/tmp'
        outbase = 'bioregion_%s' % str(time.time()).split('.')[0]
        output = os.path.join(outdir,outbase+'.json')
        if os.path.exists(output):
            raise Exception(output + " already exists")

        g.run('r.mapcalc "weighted_combined_slope =  0.01 + ' +
                            '(%s * temp_slope) + ' % self.input_temp_weight  + 
                            '(%s * lang_slope) + ' % self.input_language_weight  +
                            '(%s * precip_slope) + ' % self.input_precip_weight +
                            '(%s * biomass_slope)' % self.input_biomass_weight +
                            '"')
        g.run('r.rescale input=weighted_combined_slope output=wcr_slope to=0,100')
        g.run('r.cost -k input=wcr_slope output=cost coordinate=%s,%s max_cost=%s' % \
                (coords[0],coords[1],max_cost) )
        g.run('r.mapcalc "bioregion=if(cost >= 0)"')
        g.run('r.to.vect -s input=bioregion output=bioregion_poly feature=area')
        g.run('v.out.ogr -c input=bioregion_poly type=area format=GeoJSON dsn=%s' % output)

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

        geom.srid = settings.GEOMETRY_DB_SRID 
        g2 = geom.buffer(20000)
        geom = g2.buffer(-20000)
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
                if orig._get_FIELD_display(f) != getattr(self,f.name):
                    rerun = True
                    break
        super(MyBioregion, self).save(rerun=rerun, *args, **kwargs) 

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
