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
import threading

fields = ['temp','precip','veg','lang','elev']
user = User.objects.get(username='demo')
fldr, created = Folder.objects.get_or_create(name="Errors", user=user)

errors = [
    {
        'name': 'tim-test-a',
        'x': -119.80364990234375, 'y': 51.49445343017578,
        'marine': 10, 'veg': 1, 'temp': 50, 'lang': 47, 'precip': 0, 'size': 'S'
    },
    {
        'name': 'tim-test-b',
        'x': -119.80364990234375, 'y': 51.49445343017578,
        'marine': 0, 'veg': 1, 'temp': 50, 'lang': 47, 'precip': 0, 'size': 'S'
    },
]



def delete(): 
    a = Folder.objects.filter(user=user, name="Errors")
    a.delete()

class MyThread (threading.Thread):
    # Override Thread's __init__ method to accept the parameters needed:
    def __init__ ( self, e ):
        self.e = e
        threading.Thread.__init__ ( self )

    def run (self):
        e = self.e
        print e

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

def main():
    for e in errors:
        MyThread(e).start()
        import time
        time.sleep(2)



if __name__ == '__main__':
    delete()
    main()
