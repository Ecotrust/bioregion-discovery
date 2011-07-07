from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^analysis/', include('analysis.urls')),
    #url(r'shapefile/mpa/(?P<instances>(\d+,?)+)/$', convert_to_shp, name='mpa_shapefile'),

)
