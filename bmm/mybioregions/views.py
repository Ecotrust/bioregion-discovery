from lingcod.common import utils
from lingcod.shapes.views import ShpResponder
from lingcod.features.views import get_object_for_viewing
from django.http import HttpResponse
from django.template.defaultfilters import slugify

def bmm_shapefile(request, instances):
    from mybioregions.models import MyBioregion, Folder, BioregionShapefile
    bios = []
    for inst in instances:
        viewable, response = inst.is_viewable(request.user)
        if not viewable:
            return response

        if isinstance(inst, MyBioregion):
            inst.convert_to_shp()
            bios.append(inst)
        elif isinstance(inst, Folder):
            for bio in inst.feature_set(recurse=True,feature_classes=[MyBioregion]):
                bio.convert_to_shp()
                bios.append(bio)
        else:
            pass # ignore anything else

    filename = '_'.join([slugify(inst.name) for inst in instances])
    pks = [bio.pk for bio in bios]
    qs = BioregionShapefile.objects.filter(bio_id_num__in=pks)
    if len(qs) == 0:
        return HttpResponse(
            "Nothing in the query set; you don't want an empty shapefile", 
            status=404
        )
    shp_response = ShpResponder(qs)
    shp_response.file_name = slugify(filename[0:8])
    return shp_response()