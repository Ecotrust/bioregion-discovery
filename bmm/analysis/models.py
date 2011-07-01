from django.db import models
from django.contrib.gis.db import models
from django.conf import settings
from picklefield import PickledObjectField

# Create your models here.
    
class ReportCache(models.Model):
    wkt_hash = models.CharField(max_length=255)
    context = PickledObjectField()
    
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

class LastWild(models.Model):
    eco_name = models.CharField(max_length=99, null=True, blank=True)
    realm = models.CharField(max_length=3, null=True, blank=True)
    g200_regio = models.CharField(max_length=99, null=True, blank=True)
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    eco_code = models.CharField(max_length=50, null=True, blank=True)
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Last of the Wild")
    objects = models.GeoManager()    