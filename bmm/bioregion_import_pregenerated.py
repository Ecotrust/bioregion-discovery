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

user = User.objects.get(username='pregen')
seed = True

def delete(): 
    for model in [MyBioregion, Folder]:
        a = model.objects.all()
        for i in a:
            i.delete()

def main():
    from django.contrib.gis.gdal import DataSource
    ds = DataSource("../data/ecobio/Eco_Bioregion1.shp")
    layer = ds[0]
    layer.spatial_filter = None

    for pregen_bio in layer:
        name = "Bio%s" % pregen_bio.fid
        cont = pregen_bio.get("CONTINENT")
        if not cont: 
            continue
        folder, created = Folder.objects.get_or_create(name=cont, user=user)
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
            outg.srid = 4326
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
        if seed:
            bio.kml_safe

        bio.add_to_collection(folder)
        
def get_attendees():
    user = User.objects.get(username='pregen')
    from geopy import geocoders  
    g = geocoders.Google()

    import csv
    # Load cached
    cached = csv.reader(open("../data/cached_bioregional_players.csv",'rb'))
    cached.next()
    players = {}
    for row in cached:
        lon = row[1]
        lat = row[2]
        if "*" not in lon and "*" not in lat:
            pt = GEOSGeometry('SRID=4326;POINT(%s %s)' % (lon,lat))
        else:
            pt = None
        players[row[0]] = pt

    outcache = open("../data/cached_bioregional_players.csv",'a')
    reader = csv.reader(open("../data/bioregional_players.csv",'rb'))
    reader.next()
    for row in reader:
        name = row[0].strip()
        geoname = row[13].strip()
        if players.has_key(name):
            continue
        if not geoname:
            continue
        try:
            place, (lat, lon) = g.geocode(geoname)  
            pt = GEOSGeometry('SRID=4326;POINT(%s %s)' % (lon,lat))
            outcache.write("\"%s\",%s,%s,\"%s\"" % (name, pt.x, pt.y, geoname))
            outcache.write("\n")
        except:
            print "!!!! NO DATA FOUND FOR %s (%s)" % (name, geoname)
            outcache.write("\"%s\",******,******,\"%s\"" % (name, geoname))
            outcache.write("\n")
            pt = None

        players[name] = pt
        print pt
        print "Writing cache for %s : %s" % (name, pt)

    outcache.close()
    return players

def share(bio):
    pass


def get_bioregion(pt):
    pt = pt.transform(settings.GEOMETRY_DB_SRID, clone=True)
    bios = MyBioregion.objects.filter(user=user,output_geom__bboverlaps=pt.buffer(100000))
    for bio in bios:
        if bio.output_geom.intersects(pt):
            return bio

    # no intersection, take the closest
    nearest = 100000000000000
    the_bio = None
    for bio in bios:
        d = bio.output_geom.distance(pt)
        if d < nearest:
            nearest = d
            the_bio = bio
    return the_bio


def reports():
    req = HttpRequest()
    for bio in []: #MyBioregion.objects.filter(user=user):
        poly = bio.output_geom
        pt = GEOSGeometry('SRID=4326;POINT(%s %s)' % (x,y))
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
    public = Group.objects.get(name="Share with Public")
    #delete()
    #main()
    a = get_attendees()
    user = User.objects.get(username='pregen')
    folder, created = Folder.objects.get_or_create(name="Bioregions of the Attendees", user=user)
    for name, pt in a.items():
        if pt and len(MyBioregion.objects.filter(user=user, name=name)) < 1:
            bio = get_bioregion(pt)
            if bio:
                bio2 = bio.copy(user)
                try:
                    newname = escape(name)
                except:
                    print "NOT NAMED", name
                    newname = bio2.name
                bio2.name = newname
                bio2.input_starting_point = pt
                if seed:
                    bio2.kml_safe
                bio2.add_to_collection(folder)
                bio2.share_with(public)
                bio2.save(rerun=False)
            else:
                print "NO BIOREGION!", name
                print name, pt

