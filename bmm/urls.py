from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Include bioregions app urls
    (r'^mybioregions/', include('mybioregions.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
        
    # Include all madrona app urls. Any urls above will overwrite the common urls below
    (r'', include('madrona.common.urls')),

)

urlpatterns += patterns('',
    (r'^analysistools/', include('madrona.analysistools.urls')),
    (r'^zonal/', include('madrona.raster_stats.urls')),
)
