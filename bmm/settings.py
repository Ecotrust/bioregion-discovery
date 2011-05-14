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

# bioregions.labs.ecotrust.org 
GOOGLE_API_KEY = 'ABQIAAAAn9EXtJkKOlQBGEfk28CiahQkv7FNjWKr_TVFL7EgIFo2pXN1jRRz4grU7hzFNhpS8coxw1Dz219KfQ'
# bioregions.labs.ecotrust.org:8000
#GOOGLE_API_KEY = 'BQIAAAAn9EXtJkKOlQBGEfk28CiahTSuF7m83X3uEERz7nj3jSiHAkiaxQeB-tWbTkStcVCW35ldeO0TwWa5g'

LOG_FILE =  os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'bmm.log'))
#LOG_FILE = '/usr/local/apps/bioregions/bmm.log'
LOGFILE =  os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'bmm.log'))


from settings_local import *
