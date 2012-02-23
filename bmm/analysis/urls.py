from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    #user requested analysis
    url(r'(\w+)/(\w+)', analysis, name='analysis'),
)  
