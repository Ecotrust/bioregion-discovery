from django.db import models
from django.contrib.gis.db import models
from django.conf import settings
from picklefield import PickledObjectField

# Create your models here.
    
class ReportCache(models.Model):
    wkt_hash = models.CharField(max_length=255)
    context = PickledObjectField()
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    
    #ensure no duplicates (same geometry and type) 
    def save(self, *args, **kwargs):
        #remove any old entries
        old_entries = ReportCache.objects.filter(wkt_hash=self.wkt_hash)
        for entry in old_entries:
            ReportCache.delete(entry)
        #save the new entry
        super(ReportCache, self).save(*args, **kwargs)


class Languages(models.Model):
    nam_label = models.CharField(max_length=40)
    name_prop = models.CharField(max_length=40, null=True, blank=True)
    name2 = models.CharField(max_length=40, null=True, blank=True)
    nam_ansi = models.CharField(max_length=40, null=True, blank=True)
    cnt = models.CharField(max_length=8, null=True, blank=True)
    c1 = models.CharField(max_length=33, null=True, blank=True)
    pop = models.CharField(max_length=86, null=True, blank=True)
    lmp_pop1 = models.FloatField()
    g = models.CharField(max_length=225, null=True, blank=True)
    lmp_class = models.CharField(max_length=5, null=True, blank=True)
    familyprop = models.CharField(max_length=30, null=True, blank=True)
    family = models.CharField(max_length=30, null=True, blank=True)
    lmp_c1 = models.CharField(max_length=32, null=True, blank=True)
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Spoken Langauges")
    objects = models.GeoManager()
    
class EcoRegions(models.Model):
    area = models.FloatField()
    perimeter = models.FloatField()
    eco_name = models.CharField(max_length=99)
    realm = models.CharField(max_length=3, null=True, blank=True)
    area_km2 = models.IntegerField()
    eco_code = models.CharField(max_length=50)
    rangeland = models.CharField(max_length=50, null=True, blank=True)
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="WWF Eco-Regions")
    objects = models.GeoManager()  
    
class MarineRegions(models.Model):
    ecoregion = models.CharField(max_length=50)
    province = models.CharField(max_length=40)
    realm = models.CharField(max_length=40)
    lat_zone = models.CharField(max_length=10)
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Marine Eco-Regions")
    objects = models.GeoManager()    

class LastWild(models.Model):
    eco_name = models.CharField(max_length=99, null=True, blank=True)
    realm = models.CharField(max_length=3, null=True, blank=True)
    g200_regio = models.CharField(max_length=99, null=True, blank=True)
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    eco_code = models.CharField(max_length=50, null=True, blank=True)
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Last of the Wild")
    objects = models.GeoManager()    
    
class Watersheds(models.Model):
    maj_bas = models.IntegerField()
    maj_name = models.CharField(max_length=75)
    maj_area = models.IntegerField()
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Major Watersheds")
    objects = models.GeoManager()    
    
class WorldMask(models.Model):
    dissme = models.IntegerField()
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="World Terrestrial Mask")
    objects = models.GeoManager()    
    
class ExtinctLanguages(models.Model):
    nam_label = models.CharField(max_length=40)
    name_prop = models.CharField(max_length=40)
    name2 = models.CharField(max_length=40)
    nam_ansi = models.CharField(max_length=40)
    cnt = models.CharField(max_length=8)
    c1 = models.CharField(max_length=33)
    pop = models.CharField(max_length=86, null=True, blank=True)
    lmp_pop1 = models.FloatField()
    g = models.CharField(max_length=225)
    lmp_lon = models.FloatField()
    lmp_lat = models.FloatField()
    lmp_c1 = models.CharField(max_length=32)
    geometry = models.PointField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Extinct Language Points")
    objects = models.GeoManager()   

class SeaRise1m(models.Model):
    gridcode = models.IntegerField()
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Sea Level Rise 1m")
    objects = models.GeoManager()    

class SeaRise3m(models.Model):
    gridcode = models.IntegerField()
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Sea Level Rise 3m")
    objects = models.GeoManager()    

class SeaRise6m(models.Model):
    gridcode = models.IntegerField()
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Sea Level Rise 6m")
    objects = models.GeoManager()       

class UrbanExtent(models.Model):
    gridcode = models.IntegerField()
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Urban Extent Boundaries")
    objects = models.GeoManager()    