from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^analysis/', include('analysis.urls')),
)
