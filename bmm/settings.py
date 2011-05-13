# Django settings for bmm project.
from lingcod.common.default_settings import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIME_ZONE = 'America/Vancouver'
ROOT_URLCONF = 'bmm.urls'

GEOMETRY_DB_SRID = 54009
#KML_SIMPLIFY_TOLERANCE = .0002 #overriding this setting to account for lat/lon db srid
KML_ALTITUDEMODE_DEFAULT = 'clampToGround'

TEMPLATE_DIRS = ( os.path.realpath(os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/')), )

INSTALLED_APPS += ( 'mybioregions', 
                    'lingcod.analysistools', #necessary?
                    'django.contrib.humanize'
                  )

from settings_local import *
