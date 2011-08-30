from analysis.caching.report_caching import *
from analysis.models import WorldMask
    
def convert_sq_km_to_sq_mi(sq_km):
    return sq_km * .386102158542
    

def convert_cm_to_in(cm):
    return cm * .3937
    
def get_terra_geom(bioregion):
    if report_cache_exists(bioregion, 'terra_geom'):
        terra_geom = get_report_cache(bioregion, 'terra_geom')
    else:
        terra_mask = WorldMask.objects.get(id=1)
        terra_geom = bioregion.output_geom.intersection(terra_mask.geometry)
        create_report_cache(bioregion, dict(terra_geom=terra_geom))
    return terra_geom
    
def get_oceanic_geom(bioregion):
    if report_cache_exists(bioregion, 'oceanic_geom'):
        oceanic_geom = get_report_cache(bioregion, 'oceanic_geom')
    else:
        terra_mask = WorldMask.objects.get(id=1)
        oceanic_geom = bioregion.output_geom.difference(terra_mask.geometry)
    return oceanic_geom

'''    
def clean_geometries(model):
    objects = model.objects.all()
    num_changes = 0
    for object in objects:
        if not object.geometry.valid:
            import pdb
            pdb.set_trace()
            cleaned_geom = object.geometry.buffer(0)
            object.geometry = cleaned_geom
            object.save()
            num_changes += 1
    print '%s geometries were cleaned' %num_changes
'''
               