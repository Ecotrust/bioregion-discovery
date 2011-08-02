from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    #user requested analysis
    url(r'general_summary/(\d+)', general_summary_analysis, name='general_summary_analysis'),
    url(r'language_summary/(\d+)', language_summary_analysis, name='language_summary_analysis'),
    url(r'ecoregions_summary/(\d+)', ecoregions_summary_analysis, name='ecoregions_summary_analysis'),
    url(r'agriculture_summary/(\d+)', agriculture_summary_analysis, name='agriculture_summary_analysis'),
    url(r'summary/(\d+)', summary_analysis, name='summary_analysis'),
    url(r'climate_vulnerability/(\d+)', climate_vulnerability_analysis, name='climate_vulnerability_analysis'),
    url(r'human_vulnerability/(\d+)', human_vulnerability_analysis, name='human_vulnerability_analysis'),
    url(r'social_vulnerability/(\d+)', social_vulnerability_analysis, name='social_vulnerability_analysis'),
    url(r'vulnerability/(\d+)', vulnerability_analysis, name='vulnerability_analysis'),
)  