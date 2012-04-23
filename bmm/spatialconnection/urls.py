from django.conf.urls.defaults import *
from spatialconnection.views import *

urlpatterns = patterns('',
    #user requested analysis
    url(r'bioregions/(\w+)', bioconnect, name='bioregion-connection'),
    url(r'stories/(\w+)', storyconnect, name='story-connection'),
)  
