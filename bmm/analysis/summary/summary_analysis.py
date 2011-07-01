#from django.http import HttpResponse
from django.shortcuts import render_to_response#, get_object_or_404
from django.template import RequestContext
from lingcod.raster_stats.models import RasterDataset, zonal_stats
#from analysis.models import *
#from settings import *
from lingcod.unit_converter.models import geometry_area_in_display_units
from analysis.models import Languages, EcoRegions
from analysis.caching.report_caching import *

default_value = '---'
global_landmass = 148940000. #sq km -- see table at http://en.wikipedia.org/wiki/Earth
npp_grid_cell_size = 676000000. #sq m -- approximated via measurement tool in arcmap 
global_npp = 62000000000000000


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
    #get size of bioregion
    area = get_size(bioregion)
    #get current population (for 2010)
    population = get_population(bioregion)
    #get projected population (for 2015)
    population_2015 = get_projected_population(bioregion)
    #get list of spoken languages
    languages = get_languages(bioregion)
    #get median max temperature
    max_temp_c, max_temp_f = get_max_temp(bioregion)
    #get median min temperature
    min_temp_c, min_temp_f = get_min_temp(bioregion)
    #get mean annual temperature
    annual_temp_c, annual_temp_f = get_annual_temp(bioregion)
    #get mean annual temperature range
    annual_temp_range_c, annual_temp_range_f = get_annual_temp_range(bioregion)
    #get mean annual precipitation
    annual_precip = get_annual_precip(bioregion)
    #get existing eco-regions
    ecoregions = get_ecoregions(bioregion)
    #get land mass proportion
    landmass_perc = get_landmass_proportion(area)
    #get npp proportion
    npp_perc = get_npp_proportion(bioregion)
    #get net primary production
    avg_npp = get_avg_npp(bioregion)
    #get soil suitability
    soil_suitability = get_soil_suitability(bioregion)    
    #compile context
    context = {'bioregion': bioregion, 'default_value': default_value, 'area': area, 'population': population, 'population_2015': population_2015, 'languages': languages, 'max_temp_c': max_temp_c, 'max_temp_f': max_temp_f, 'min_temp_c': min_temp_c, 'min_temp_f': min_temp_f, 'annual_temp_c': annual_temp_c, 'annual_temp_f': annual_temp_f, 'annual_temp_range_c': annual_temp_range_c, 'annual_temp_range_f': annual_temp_range_f, 'annual_precip': annual_precip, 'ecoregions': ecoregions, 'landmass_perc': landmass_perc, 'soil_suitability': soil_suitability, 'avg_npp': avg_npp, 'npp_perc': npp_perc}
    return context
    #get average poverty index
    #poverty = get_poverty(bioregion)
    #get soil moisture
    #soil_moisture = get_soil_moisture(bioregion)
    
           
def get_size(bioregion):
    area = int(round(geometry_area_in_display_units(bioregion.output_geom)))
    return area
           
def get_population(bioregion):
    pop_geom = RasterDataset.objects.get(name='population_2010')
    pop_stats = zonal_stats(bioregion.output_geom, pop_geom)
    return int(pop_stats.sum)

def get_projected_population(bioregion):
    pop_geom = RasterDataset.objects.get(name='population_2015')
    pop_stats = zonal_stats(bioregion.output_geom, pop_geom)
    return int(pop_stats.sum)
   
def get_languages(bioregion):
    if report_cache_exists(bioregion, 'languages'):
        language_names = get_report_cache(bioregion, 'languages')
        return language_names
    else:
        languages = Languages.objects.all()
        language_tuples = [(language.geometry.intersection(bioregion.output_geom).area, language.nam_ansi) for language in languages if language.geometry.intersects(bioregion.output_geom)]
        language_dict = {}
        for area,name in language_tuples:
            if name in language_dict.keys():
                language_dict[name] += area
            else:
                language_dict[name] = area
        language_tuples = [(area, name) for name,area in language_dict.items()]
        language_tuples.sort(reverse=True)
        language_names = [name for (area, name) in language_tuples]
        create_report_cache(bioregion, dict(languages=language_names))
        return language_names
       
def get_max_temp(bioregion):
    max_temp_geom = RasterDataset.objects.get(name='max_temp')
    max_temp_stats = zonal_stats(bioregion.output_geom, max_temp_geom)
    max_temp_c = max_temp_stats.avg / 10
    max_temp_f = max_temp_c * 9 / 5. + 32
    return max_temp_c, max_temp_f
   
def get_min_temp(bioregion):
    min_temp_geom = RasterDataset.objects.get(name='min_temp')
    min_temp_stats = zonal_stats(bioregion.output_geom, min_temp_geom)
    min_temp_c = min_temp_stats.avg / 10
    min_temp_f = min_temp_c * 9 / 5. + 32
    return min_temp_c, min_temp_f
    
def get_annual_temp(bioregion):
    temp_geom = RasterDataset.objects.get(name='annual_temperature')
    temp_stats = zonal_stats(bioregion.output_geom, temp_geom)
    temp_c = temp_stats.avg / 10
    temp_f = temp_c * 9 / 5. + 32
    return temp_c, temp_f
    
def get_annual_temp_range(bioregion):
    temp_range_geom = RasterDataset.objects.get(name='temp_range')
    temp_range_stats = zonal_stats(bioregion.output_geom, temp_range_geom)
    temp_range_c = temp_range_stats.avg / 10
    temp_range_f = temp_range_c * 9 / 5. + 32
    return temp_range_c, temp_range_f
    
def get_annual_precip(bioregion):
    precip_geom = RasterDataset.objects.get(name='annual_precipitation')
    precip_stats = zonal_stats(bioregion.output_geom, precip_geom)
    return precip_stats.avg / 10
    
def get_ecoregions(bioregion):
    if report_cache_exists(bioregion, 'ecoregions'):
        ecoregion_names = get_report_cache(bioregion, 'ecoregions')
        return ecoregion_names
    else:
        ecoregions = EcoRegions.objects.all()
        ecoregion_tuples = [(ecoregion.geometry.intersection(bioregion.output_geom).area, ecoregion.eco_name) for ecoregion in ecoregions if ecoregion.geometry.intersects(bioregion.output_geom)]
        ecoregion_dict = {}
        for area,name in ecoregion_tuples:
            if name in ecoregion_dict.keys():
                ecoregion_dict[name] += area
            else:
                ecoregion_dict[name] = area
        ecoregion_tuples = [(area, name) for name,area in ecoregion_dict.items()]
        ecoregion_tuples.sort(reverse=True)
        ecoregion_names = [name for (area, name) in ecoregion_tuples]
        create_report_cache(bioregion, dict(ecoregions=ecoregion_names))
        #just return the following for now (until we get caching in place)
        #ecoregion_names = ['Central and Southern Cascades forests', 'Central Pacific coastal forests', 'Willamette Valley forests', 'Puget lowland forests', 'Eastern Cascades forests', 'Klamath-Siskiyou forests', 'Snake-Columbia shrub steppe', 'Blue Mountains forests']
        return ecoregion_names    
    
def get_landmass_proportion(area):
    perc = area / global_landmass
    return perc
    
def get_soil_suitability(bioregion):
    suit_geom = RasterDataset.objects.get(name='soil_suitability')
    suit_stats = zonal_stats(bioregion.output_geom, suit_geom)
    return suit_stats.avg

def get_npp_proportion(bioregion):
    npp_geom = RasterDataset.objects.get(name='npp')
    npp_stats = zonal_stats(bioregion.output_geom, npp_geom)
    return npp_stats.sum / global_npp
    
def get_avg_npp(bioregion):
    npp_geom = RasterDataset.objects.get(name='npp')
    npp_stats = zonal_stats(bioregion.output_geom, npp_geom)
    return npp_stats.avg / npp_grid_cell_size

    
def get_poverty(bioregion):
    return default_value
    poverty_geom = RasterDataset.objects.get(name='poverty')
    poverty_stats = zonal_stats(bioregion.output_geom, poverty_geom)
    return poverty_stats.avg

def get_soil_moisture(bioregion):
    soilmoist_geom = RasterDataset.objects.get(name='soil_moisture')
    soilmoist_stats = zonal_stats(bioregion.output_geom, soilmoist_geom)
    return soilmoist_stats.avg
