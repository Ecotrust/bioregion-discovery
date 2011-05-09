from lingcod.features.forms import FeatureForm, SpatialFeatureForm
from mybioregions.models import MyBioregion, Folder

class MyBioregionForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
        model = MyBioregion

class FolderForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = Folder
