#from django.http import HttpResponse
from django.shortcuts import render_to_response#, get_object_or_404
from django.template import RequestContext
from lingcod.raster_stats.models import RasterDataset, zonal_stats
#from analysis.models import *
#from settings import *

default_value = '---'

'''
Runs analysis for Summary report
Called by analysis.views.summary_analysis
'''
def display_summary_analysis(request, bioregion, template='summary_report.html'):
    context = run_summary_analysis(bioregion)
    return render_to_response(template, RequestContext(request, context)) 
     
'''
Run the analysis, create the cache, and return the results as a context dictionary so they may be rendered with template
'''    
def run_summary_analysis(bioregion):
    #get total population 
    population = get_population(bioregion)
    #get average poverty index
    poverty = get_poverty(bioregion)
    #get soil suitability
    soil_suitability = get_soil_suitability(bioregion)
    #get soil moisture
    soil_moisture = get_soil_moisture(bioregion)
    #get net primary production
    npp = get_npp(bioregion)
    #compile context
    context = {'bioregion': bioregion, 'default_value': default_value, 'population': population, 'poverty': poverty, 'soil_suitability': soil_suitability, 'soil_moisture': soil_moisture, 'npp': npp}
    return context
           
def get_population(bioregion):
    pop_geom = RasterDataset.objects.get(name='population')
    pop_stats = zonal_stats(bioregion.output_geom, pop_geom)
    return int(pop_stats.sum)
   
def get_poverty(bioregion):
    return default_value
    poverty_geom = RasterDataset.objects.get(name='poverty')
    poverty_stats = zonal_stats(bioregion.output_geom, poverty_geom)
    return poverty_stats.avg

def get_soil_suitability(bioregion):
    suit_geom = RasterDataset.objects.get(name='soil_suitability')
    suit_stats = zonal_stats(bioregion.output_geom, suit_geom)
    return suit_stats.avg

def get_soil_moisture(bioregion):
    soilmoist_geom = RasterDataset.objects.get(name='soil_moisture')
    soilmoist_stats = zonal_stats(bioregion.output_geom, soilmoist_geom)
    return soilmoist_stats.avg

def get_npp(bioregion):
    npp_geom = RasterDataset.objects.get(name='npp')
    npp_stats = zonal_stats(bioregion.output_geom, npp_geom)
    return npp_stats.avg
