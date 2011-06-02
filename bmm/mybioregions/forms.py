from lingcod.features.forms import FeatureForm, SpatialFeatureForm
from mybioregions.models import MyBioregion, Folder
from lingcod.analysistools.widgets import SliderWidget
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.gis.geos import fromstr
from models import *

class SimplePointInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        type = 'point'
        output = super(SimplePointInput, self).render(name, value, attrs)
        set_text = "Set"
        new_text = "New"
        if value:
            geo = fromstr(value)
            set_text = "Reset"
            new_text = "Reset"
            print geo
        return mark_safe("""
        <div>
            <a id="do_grabpoint" class="button" href="#">
                <span>Click to %s Starting Point</span>
            </a>
            <span style="display:none"> 
            %s 
            </span>
        </div>
        <script type="text/javascript">
        var shape;

        lingcod.beforeDestroy( function() {
            if(shape && shape.getParentNode()){
                gex.dom.removeObject(shape);
            }
        });

        lingcod.onShow( function() {
            function shape_to_wkt(shape) {
                var lat = shape.getGeometry().getLatitude();
                var lon = shape.getGeometry().getLongitude();
                var wkt = "POINT(" + lon + " " + lat + ")";
                return wkt;
            }

            $('#do_grabpoint').click( function () {
                if(!$(this).hasClass('disabled')){
                    if(shape && shape.getParentNode()){
                        gex.dom.removeObject(shape);
                    }
                    $(this).addClass('disabled');
                    var button = $(this);
                    button.html('<span>Click map to set placemark</span>');

                    var popts = {
                        visibility: true,
                        name: '%s Bioregion Starting Point',
                        style: { icon: { color: '#FF0' } }            
                    }
                    popts['point'] = [0,0]; 
                    shape = gex.dom.addPlacemark(popts);
                    gex.edit.place(shape, {
                        bounce: false,
                        dropCallback: function(){
                            $('#id_%s').val(shape_to_wkt(shape));
                            button.html('<span>Drag Placemark to Reset</span>');
                            gex.edit.makeDraggable(shape, {
                                bounce: false, 
                                dropCallback: function () {
                                    $('#id_%s').val(shape_to_wkt(shape));
                                }
                            });
                        }
                    });
                }
            });
        });
        </script>
        """ % (set_text,output,new_text,name,name))

class MyBioregionForm(FeatureForm):
    #might change the following to ModelChoiceField to pull city names from a model
    #also, might use different strategy altogether that allows users to simply select a point on a map as the starting point
    input_starting_point = forms.CharField(widget=SimplePointInput())
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
