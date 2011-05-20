from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from mybioregions.models import MyBioregion

'''
Accessed via named url when user selects Results, Summary on their bioregion 
'''
def summary_analysis(request, bioregion_id):
    from summary.summary_analysis import display_summary_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_summary_analysis(request, bioregion)
    
'''
Accessed via named url when user selects Results, Vulnerabilities on their bioregion 
'''
def vulnerability_analysis(request, bioregion_id):
    from vulnerability.vulnerability_analysis import display_vulnerability_analysis
    bioregion = get_object_or_404(MyBioregion, pk=bioregion_id)
    return display_vulnerability_analysis(request, bioregion)
    
