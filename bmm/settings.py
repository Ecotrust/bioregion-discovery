# Django settings for bmm project.
from lingcod.common.default_settings import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIME_ZONE = 'America/Vancouver'
ROOT_URLCONF = 'bmm.urls'

GEOMETRY_DB_SRID = 4326
KML_SIMPLIFY_TOLERANCE = .0002 #overriding this setting to account for lat/lon db srid
KML_ALTITUDEMODE_DEFAULT = 'clampToGround'

INSTALLED_APPS += ( 'mybioregions', )

from settings_local import *
