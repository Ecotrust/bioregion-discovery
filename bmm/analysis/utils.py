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
               