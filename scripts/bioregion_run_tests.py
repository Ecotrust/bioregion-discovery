from django.core.management import setup_environ
import os
import sys
sys.path.append(os.path.dirname(__file__))

import settings
setup_environ(settings)

#==================================#
from mybioregions.models import *
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.auth.models import User, Group
from lingcod.analysistools.grass import Grass
from lingcod.analysistools.utils import linear_regression
import random

errors = [
    {
        'name': 'Ryans polar',
        'x': -135.186,
        'y': -89.946,
        'marine': 88,
        'size': 'VL'
    },
    {
        'name': 'Scotts Failed sahara shape',
        'x': 14.7278003692, 'y': 21.2676792145,
        'marine': 0, 'veg': 81, 'temp': 77, 'lang': 23, 'precip': 83, 'size': 'L'
    },
    {
        'name': 'tim-test-b',
        'x': -119.80364990234375, 'y': 51.49445343017578,
        'marine': 0, 'veg': 1, 'temp': 50, 'lang': 47, 'precip': 0, 'size': 'S'
    },
]

user = User.objects.get(username='demo')

errors = [e for e in errors if e['name'].startswith('tim')]

def delete(): 
    a = Folder.objects.filter(user=user, name="Errors")
    a.delete()

def main():
    fields = ['temp','precip','veg','lang','elev']
    fldr, created = Folder.objects.get_or_create(name="Errors", user=user)

    for e in errors:
        for f in fields:
            if not e.has_key(f):
                e[f] = 50
        
        g = GEOSGeometry('SRID=4326;POINT(%s %s)' % (e['x'],e['y']))
        bio = MyBioregion(user=user, 
                name=e['name'], 
                input_temp_weight = e['temp'],
                input_precip_weight = e['precip'],
                input_biomass_weight = e['veg'],
                input_lang_weight = e['lang'],
                input_elev_weight = e['elev'],
                input_marine_weight = e['marine'], 
                input_starting_point = g,
                input_bioregion_size= e['size']
                ) 
        bio.save()
        bio.add_to_collection(fldr)
        del bio

if __name__ == '__main__':
    delete()
    main()
