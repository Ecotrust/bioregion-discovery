from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    #user requested analysis
    url(r'summary/(\d+)', summary_analysis, name='summary_analysis'),
    url(r'vulnerability/(\d+)', vulnerability_analysis, name='vulnerability_analysis'),
)  