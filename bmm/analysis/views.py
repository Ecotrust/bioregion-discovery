from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from mybioregions.models import MyBioregion

'''
Accessed via named url when user selects Summary, General on their bioregion 
'''
def general_summary_analysis(request, bioregion_id):
    from summary.summary_analysis import display_general_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_general_analysis(request, bioregion)
    
'''
Accessed via named url when user selects Summary, Language on their bioregion 
'''
def language_summary_analysis(request, bioregion_id):
    from summary.summary_analysis import display_language_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_language_analysis(request, bioregion)
    
'''
Accessed via named url when user selects Summary, Eco-Regions on their bioregion 
'''
def ecoregions_summary_analysis(request, bioregion_id):
    from summary.summary_analysis import display_ecoregions_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_ecoregions_analysis(request, bioregion)
    
'''
Accessed via named url when user selects Summary, Agriculture on their bioregion 
'''
def agriculture_summary_analysis(request, bioregion_id):
    from summary.summary_analysis import display_agriculture_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_agriculture_analysis(request, bioregion)
    
'''
Accessed via named url when user selects Results, Summary on their bioregion 
'''
def summary_analysis(request, bioregion_id):
    from summary.summary_analysis import display_summary_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_summary_analysis(request, bioregion)
    
'''
Accessed via named url when user selects Vulnerabilities, Climate on their bioregion 
'''
def climate_vulnerability_analysis(request, bioregion_id):
    from vulnerability.vulnerability_analysis import display_climate_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_climate_analysis(request, bioregion)
    
'''
Accessed via named url when user selects Vulnerabilities, Climate on their bioregion 
'''
def socioeconomic_vulnerability_analysis(request, bioregion_id):
    from vulnerability.vulnerability_analysis import display_socioeconomic_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_socioeconomic_analysis(request, bioregion)
    
'''
Accessed via named url when user selects Vulnerabilities, Climate on their bioregion 
'''
def hazards_vulnerability_analysis(request, bioregion_id):
    from vulnerability.vulnerability_analysis import display_hazards_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_hazards_analysis(request, bioregion)
    
'''
Accessed via named url when user selects Results, Vulnerabilities on their bioregion 
'''
def vulnerability_analysis(request, bioregion_id):
    from vulnerability.vulnerability_analysis import display_vulnerability_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_vulnerability_analysis(request, bioregion)
    
