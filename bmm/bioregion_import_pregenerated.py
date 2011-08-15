from django.core.management import setup_environ
import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

import settings
setup_environ(settings)

#==================================#
from mybioregions.models import *
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.auth.models import User, Group
from lingcod.analysistools.utils import linear_regression
from django.conf import settings
from analysis.views import *
from django.http import HttpRequest
import random
from IPython.Shell import IPShellEmbed; debug = IPShellEmbed()

lines = open("../data/cities15000.txt").readlines()

def get_random_city():
    line = random.choice(lines)
    data = line.strip().split('\t')
    return float(data[5]), float(data[4]), data[1]

def delete(): 
    for model in [MyBioregion, Folder]:
        a = model.objects.all()
        for i in a:
            i.delete()

def main():
    user = User.objects.get(username='pregen')

    from django.contrib.gis.gdal import DataSource
    ds = DataSource("../data/ecobio/Eco_Bioregion1.shp")
    layer = ds[0]
    layer.spatial_filter = None

    # TODO loop through delegate list
    for i in range(20):
        #x,y,name = get_delegate_info()
        x,y,name = get_random_city()
        g = GEOSGeometry('SRID=4326;POINT(%s %s)' % (x,y))

        # intersect pregen bioregions with g to get a single polygon
        extent = g.buffer(0.0000001).extent
        print extent
        layer.spatial_filter = extent
        try:
            pregen_bio = [feat for feat in layer][0]
        except IndexError:
            print "-- Point doesnt intersect any bioregions; skipping !!!!!"
            print x, y, name

        if len(layer) > 1:
            print "-- Point is right in between two bioregions; use the first !!!!!"

        outg = None
        if pregen_bio.geom.geom_count > 1:
            for geom in pregen_bio.geom:
                if geom.geos.intersects(g):
                    outg = geom.geos
        else:
            outg = pregen_bio.geom.geos

        if outg:
            outg.srid = 4326

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
                input_bioregion_size= 'VS'
                ) 
        bio.save()

        # Now override the size and geometry
        bio.input_bioregion_size = 'L'
        bio.output_geom = outg.transform(settings.GEOMETRY_DB_SRID, clone=True)
        bio.satisfied = True
        bio.save(rerun=False)


def reports():
    user = User.objects.get(username='pregen')
    req = HttpRequest()
    for bio in MyBioregion.objects.all(user=user):
        print "reports for ", bio.name
        overview_analysis(req, bio.pk)
        language_analysis(req, bio.pk)
        natural_resources_analysis(req, bio.pk)
        agriculture_analysis(req, bio.pk)
        summary_analysis(req, bio.pk)
        climate_change_analysis(req, bio.pk)
        socioeconomic_analysis(req, bio.pk)
        natural_hazards_analysis(req, bio.pk)
        vulnerability_analysis(req, bio.pk)


if __name__ == '__main__':
    delete()
    main()
    reports()
