from madrona.features.forms import FeatureForm, SpatialFeatureForm
from mybioregions.models import MyBioregion, Folder
from madrona.analysistools.widgets import SliderWidget, SimplePoint
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.gis.geos import fromstr
#from django.forms.widgets import RadioSelect
from models import *

class MyBioregionForm(FeatureForm):
    #might change the following to ModelChoiceField to pull city names from a model
    #also, might use different strategy altogether that allows users to simply select a point on a map as the starting point
    input_starting_point = forms.CharField(label="Bioregion Starting Point", widget=SimplePoint(title="Bioregion"))
    input_temp_weight = forms.FloatField(min_value=0, max_value=100.0, initial=50,
            widget=SliderWidget(min=0,max=100,step=1, show_number=False, image='bmm/img/sun.png'),
            label="Temperature")
    input_precip_weight = forms.FloatField(min_value=0, max_value=100.0, initial=50,
            widget=SliderWidget(min=0,max=100,step=1, show_number=False, image='bmm/img/rain.png'),
            label="Precipitation")
    input_biomass_weight = forms.FloatField(min_value=0, max_value=100.0, initial=50,
            widget=SliderWidget(min=0,max=100,step=1, show_number=False, image='bmm/img/veg.png'),
            label="Vegetation")
    input_lang_weight = forms.FloatField(min_value=0, max_value=100.0, initial=50,
            widget=SliderWidget(min=0,max=100,step=1, show_number=False, image='bmm/img/lang.png'),
            label="Human Language")
    input_elev_weight = forms.FloatField(min_value=0, max_value=100.0, initial=50,
            widget=SliderWidget(min=0,max=100,step=1, show_number=False, image='bmm/img/elev.png'),
            label="Elevation")
    input_marine_weight = forms.FloatField(min_value=0, max_value=100.0, initial=0,
            widget=SliderWidget(min=0,max=100,step=1, show_number=False, image='bmm/img/marine.png'),
            label="Marine Environment")
    #input_dwater_weight = forms.FloatField(min_value=0, max_value=100.0, initial=50,
    #        widget=SliderWidget(min=0,max=100,step=1, show_number=False, image='bmm/img/dwater.png'),
    #        label="Proximity to Major Waterbodies")
        
    class Meta(FeatureForm.Meta):
        model = MyBioregion
        exclude = list(FeatureForm.Meta.exclude)
        for f in model.output_fields():
            exclude.append(f.attname)

class FolderForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = Folder
    
class DrawnBioregionForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
        model = DrawnBioregion
