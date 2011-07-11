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
        const1 = 2000
        max_cost = x * const1 / t_weight

        desired_size_mHa = 100 #million Hectares
        desired_size = 10000000000 * desired_size_mHa

        # set initial region
        g.run('g.region rast=soilmoist')
        g.run('r.mapcalc "weighted_combined_slope = 0.5 + ' +
                            '(%s * temp_slope) + ' % p_temp  + 
                            '(%s * lang_slope) + ' % p_language +
                            '(%s * precip_slope) + ' % p_precip +
                            '(%s * biomass_slope)' % p_biomass +
                            '"')

        ################# Run #2 - adjusted cost #####################
        ratio = 0.0
        i = 0
        overs = []
        unders = []
        while ratio < 0.9 or ratio > 1.1:
            g.run('g.region n=7078485 s=3660936 e=-7024061 w=-10560592')
            g.run('r.cost -k input=weighted_combined_slope output=cost1 coordinate=%s,%s max_cost=%s' % \
                    (coords[0],coords[1],max_cost) )
            g.run('r.mapcalc "bioregion1=if(cost1 >= 0)"')
            g.run('r.to.vect input=bioregion1 output=bioregion1_poly feature=area') # -s
            if os.path.exists(output):
                os.remove(output)
            g.run('v.out.ogr -c input=bioregion1_poly type=area format=GeoJSON dsn=%s' % output)
            largest_area, geom = get_largest_from_json(output)

            ratio = desired_size/largest_area
            if ratio < 1.0 : 
                overs.append(max_cost)
            else:
                unders.append(max_cost)

            print "# run #", i, "ratio", int(ratio*100),"%", "max cost", int(max_cost)
            print "   # actual size", int((largest_area/10000.0)/1000000.0)
            print "   # desired_size", int((desired_size/10000.0)/1000000.0)
            try:
                max_cost = (max(unders) + min(overs))/2.0
            except ValueError:
                max_cost = max_cost * (ratio ** 0.5)
            i = i+1


        geom.srid = settings.GEOMETRY_DB_SRID 
        if geom and not settings.DEBUG:
            os.remove(output)
            del g
        self.output_geom = geom
        return True
        
    def save(self, *args, **kwargs):
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
