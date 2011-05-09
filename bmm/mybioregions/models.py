from django.db import models
from lingcod.features.models import PolygonFeature, FeatureCollection
from lingcod.features import register

@register
class MyBioregion(PolygonFeature):
    class Options:
        form = 'bmm.mybioregions.forms.MyBioregionForm'

@register
class Folder(FeatureCollection):
    class Options:
        form = 'bmm.mybioregions.forms.FolderForm'
        valid_children = (
            'bmm.mybioregions.models.MyBioregion',
            'bmm.mybioregions.models.Folder',
        )
