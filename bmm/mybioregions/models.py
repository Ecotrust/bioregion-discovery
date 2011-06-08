from django.conf import settings
from django.db import models
from django.contrib.gis.db import models
from django.utils.html import escape
from lingcod.features.models import PolygonFeature, FeatureCollection
from lingcod.analysistools.models import Analysis
from lingcod.features import register
from lingcod.common.utils import asKml
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
        max_cost=1

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

        g.run('r.mapcalc "weighted_combined_slope = ' +
                            '(%s * temp_slope) + ' % self.input_temp_weight  + 
                            '(%s * lang_slope) + ' % self.input_language_weight  +
                            '(%s * precip_slope) + ' % self.input_precip_weight +
                            '(%s * biomass_slope)' % self.input_biomass_weight +
                            '"')
        g.run('r.cost input=weighted_combined_slope output=cost coordinate=%s,%s max_cost=%s' % \
                (coords[0],coords[1],max_cost) )
        g.run('r.mapcalc "bioregion=if(cost >= 0)"')
        g.run('r.to.vect -s input=bioregion output=bioregion_poly feature=area')
        g.run('v.out.ogr -c input=bioregion_poly type=area format=GeoJSON dsn=%s' % output)

        from django.contrib.gis.gdal import DataSource
        ds = DataSource(output)
        layer = ds[0]
        geom = layer[0].geom.geos
        geom.srid = settings.GEOMETRY_DB_SRID 

        self.output_geom = geom #placeholder.geometry_final
        placeholder_name = 'portland placeholder'
        placeholder = Placeholder.objects.get(name=placeholder_name)
        return True
        
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
    
    class Options:
        verbose_name = 'Bioregion'
        icon_url = 'bmm/img/regions.png'
        form = 'mybioregions.forms.MyBioregionForm'
        form_template = 'mybioregion/form.html'
        show_template = 'mybioregion/show.html'

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
       
class Placeholder(PolygonFeature):
    description = models.TextField(default="", null=True, blank=True)

    class Options:
        manipulators = []
        verbose_name = 'Bioregion Placeholder'
        form = 'mybioregions.forms.PlaceholderForm'
        show_template = 'placeholder/show.html'
      
