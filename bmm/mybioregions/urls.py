from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'^analysis/', include('analysis.urls')),
    (r'^finished/(?P<uid>[\w_]+)/', finished ),
)
