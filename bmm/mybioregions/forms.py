from lingcod.features.forms import FeatureForm, SpatialFeatureForm
from mybioregions.models import MyBioregion, Folder
from lingcod.analysistools.widgets import SliderWidget, SimplePoint
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.gis.geos import fromstr
from models import *

class MyBioregionForm(FeatureForm):
    #might change the following to ModelChoiceField to pull city names from a model
    #also, might use different strategy altogether that allows users to simply select a point on a map as the starting point
    input_starting_point = forms.CharField(label="Bioregion Starting Point", widget=SimplePoint(title="Bioregion"))
    input_temp_weight = forms.FloatField(min_value=0, max_value=1.0, initial=0.5,
            widget=SliderWidget(min=0,max=1,step=0.01,image='bmm/img/sun.png'),
            label="Value given to Temperature")
    input_language_weight = forms.FloatField(min_value=0, max_value=1.0, initial=0.5,
            widget=SliderWidget(min=0,max=1,step=0.01,image='bmm/img/lang.png'),
            label="Value given to Spoken Language")
    input_precip_weight = forms.FloatField(min_value=0, max_value=1.0, initial=0.5,
            widget=SliderWidget(min=0,max=1,step=0.01,image='bmm/img/rain.png'),
            label="Value given to Precipitation")
    input_biomass_weight = forms.FloatField(min_value=0, max_value=1.0, initial=0.5,
            widget=SliderWidget(min=0,max=1,step=0.01,image='bmm/img/veg.png'),
            label="Value given to Vegetation")
        
    class Meta(FeatureForm.Meta):
        model = MyBioregion
        exclude = list(FeatureForm.Meta.exclude)
        for f in model.output_fields():
            exclude.append(f.attname)

class FolderForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = Folder
    
class PlaceholderForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
        model = Placeholder
