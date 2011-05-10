from lingcod.features.forms import FeatureForm, SpatialFeatureForm
from mybioregions.models import MyBioregion, Folder
from lingcod.analysistools.widgets import SliderWidget
from django import forms
from models import *

class MyBioregionForm(SpatialFeatureForm):
    #might change the following to ModelChoiceField to pull city names from a model
    #also, might use different strategy altogether that allows users to simply select a point on a map as the starting point
    input_start_point = forms.ChoiceField(label="Population Center", 
            choices=([('San Diego', 'San Diego'), ('Portland', 'Portland'), ('Denver', 'Denver')]), 
            initial='Portland', required=True)
    input_temp_weight = forms.FloatField(min_value=0, max_value=1.0, initial=0.5,
            widget=SliderWidget(min=0,max=1,step=0.01),
            label="Value given to Temperature")
    input_language_weight = forms.FloatField(min_value=0, max_value=1.0, initial=0.5,
            widget=SliderWidget(min=0,max=1,step=0.01),
            label="Value given to Spoken Language")
    input_precip_weight = forms.FloatField(min_value=0, max_value=1.0, initial=0.5,
            widget=SliderWidget(min=0,max=1,step=0.01),
            label="Value given to Precipitation")
    input_biomass_weight = forms.FloatField(min_value=0, max_value=1.0, initial=0.5,
            widget=SliderWidget(min=0,max=1,step=0.01),
            label="Value given to Vegetation")
        
    class Meta(SpatialFeatureForm.Meta):
        model = MyBioregion

class FolderForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = Folder
