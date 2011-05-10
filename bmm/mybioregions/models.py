from django.db import models
from lingcod.features.models import PolygonFeature, FeatureCollection
from lingcod.features import register

@register
class MyBioregion(PolygonFeature):
    input_start_point = models.TextField(verbose_name='Population Center')
    input_temp_weight = models.FloatField(verbose_name='Value given to Temperature')
    input_language_weight = models.FloatField(verbose_name='Value given to Spoken Language')
    input_precip_weight = models.FloatField(verbose_name='Value given to Precipitation')
    input_biomass_weight = models.FloatField(verbose_name='Value given to Vegetation')
    description = models.TextField(null=True, blank=True)
    class Options:
        verbose_name = 'Bioregion'
        form = 'mybioregions.forms.MyBioregionForm'
        form_template = 'mybioregions/form.html'
        show_template = 'mybioregions/show.html'

@register
class Folder(FeatureCollection):
    class Options:
        form = 'mybioregions.forms.FolderForm'
        valid_children = (
            'bmm.mybioregions.models.MyBioregion',
            'bmm.mybioregions.models.Folder',
        )
