from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    #user requested analysis
    url(r'overview/(\d+)', overview_analysis, name='overview_analysis'),
    url(r'language/(\d+)', language_analysis, name='language_analysis'),
    url(r'natural_resources/(\d+)', natural_resources_analysis, name='natural_resources_analysis'),
    #url(r'agriculture/(\d+)', agriculture_analysis, name='agriculture_analysis'),
    url(r'summary/(\d+)', summary_analysis, name='summary_analysis'),
    url(r'climate_change/(\d+)', climate_change_analysis, name='climate_change_analysis'),
    url(r'socioeconomic/(\d+)', socioeconomic_analysis, name='socioeconomic_analysis'),
    url(r'natural_hazards/(\d+)', natural_hazards_analysis, name='natural_hazards_analysis'),
    url(r'vulnerability/(\d+)', vulnerability_analysis, name='vulnerability_analysis'),
)  