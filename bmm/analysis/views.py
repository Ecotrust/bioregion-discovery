from django.http import Http404
from mybioregions.models import MyBioregion, DrawnBioregion
from madrona.features import get_feature_by_uid

# Analysis methods
# should be imported as display_<atype>_analysis function
from analysis.summary.summary_analysis import display_general_analysis as display_overview_analysis #TODO
from analysis.summary.summary_analysis import display_language_analysis
from analysis.summary.summary_analysis import display_resources_analysis
#from analysis.summary.summary_analysis import display_agriculture_analysis
from analysis.summary.summary_analysis import display_summary_analysis
from analysis.vulnerability.vulnerability_analysis import display_climate_analysis
from analysis.vulnerability.vulnerability_analysis import display_socioeconomic_analysis
from analysis.vulnerability.vulnerability_analysis import display_hazards_analysis
#from analysis.vulnerability.vulnerability_analysis import display_vulnerability_analysis

def get_bioregion(uid):
    '''
    Gets the bioregions instance for a given uid
    '''
    try:
        return get_feature_by_uid(uid) 
    except:
        raise Http404('UID %s does not exist' % uid)

def analysis(request, atype, uid):
    # Get the function by name
    # Must be a display_<atype>_analysis function in the scope
    try:
        func = globals()['display_%s_analysis' % atype]
    except KeyError:
        raise Http404('Analysis method `%s` is unknown' % atype)
    bioregion = get_bioregion(uid)
    return func(request, bioregion)
