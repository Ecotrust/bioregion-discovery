from django.core.management import setup_environ
import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

import settings
setup_environ(settings)

from mybioregions.models import *
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.auth.models import User, Group
import random
user = User.objects.get(username='sfletche')


def main():
    try:
        shapefile = sys.argv[1]
        name = sys.argv[2]
    except:
        print 
        print 'This script takes 2 arguments, the path to the shapefile and the name that should be assigned to this shapefile.'
        print
        print 'python bioregion_import_oneoff.py ..\data\bioregion_shps\micronesia.shp Micronesia'
        print
        return
    try:
        x = sys.argv[3]
        y = sys.argv[4]
        xy = True
    except:
        xy = False
    from django.contrib.gis.gdal import DataSource
    #ds = DataSource("../data/bioregion_shps/micronesia.shp")
    ds = DataSource(shapefile)
    layer = ds[0]
    layer.spatial_filter = None
    
    for pregen_bio in layer:
        #name = "Micronesia" 
        folder, created = Folder.objects.get_or_create(name='additional profiles', user=user)
        if xy:
            g = GEOSGeometry('SRID=54009;POINT(%s %s)' %(x,y))
        else:
            g = pregen_bio.geom.geos.point_on_surface #GEOSGeometry('SRID=4326;POINT(%s %s)' % (x,y))
        

        outg = None
        if pregen_bio.geom.geom_type == 'MultiPolygon':
            largestarea = 0
            for geom in pregen_bio.geom:
                if geom.area > largestarea:
                    largestarea = geom.area
                    outg = geom.geos
        elif pregen_bio.geom.geom_type == 'Polygon':
            outg = pregen_bio.geom.geos
        else:
            print "!!!! not a polygon"
            continue

        if outg:
            outg.srid = 54009
        else:
            debug()

        desired_size = random.choice(SIZE_LOOKUP.keys())
        desired_size_mHa = SIZE_LOOKUP[desired_size]
        bio = MyBioregion(user=user, name=name, 
                input_temp_weight = 50,
                input_precip_weight = 50,
                input_biomass_weight = 50,
                input_lang_weight = 50,
                input_elev_weight = 50,
                input_marine_weight = 10,
                input_starting_point = g,
                input_bioregion_size= 'L'
                ) 

        # Now override the size and geometry
        bio.output_geom = outg.transform(settings.GEOMETRY_DB_SRID, clone=True)
        bio.output_numruns = 5
        bio.output_finalcost = 100
        bio.satisfied = True
        bio.save(rerun=False)
        bio.kml_safe

        bio.add_to_collection(folder)

if __name__ == "__main__":
    main()        