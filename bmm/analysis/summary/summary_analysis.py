#from django.http import HttpResponse
from django.shortcuts import render_to_response#, get_object_or_404
from django.template import RequestContext
from lingcod.raster_stats.models import RasterDataset, zonal_stats
#from analysis.models import *
#from settings import *
from lingcod.unit_converter.models import geometry_area_in_display_units, convert_float_to_area_display_units
from analysis.models import Languages, EcoRegions, LastWild, MarineRegions
from analysis.caching.report_caching import *
from lingcod.common.utils import clean_geometry

default_value = '---'
global_landmass = 148940000. #sq km -- see table at http://en.wikipedia.org/wiki/Earth
npp_grid_cell_size = 676000000. #sq m -- approximated via measurement tool in arcmap 
global_npp = 62000000000000000 #need to re-figure this value (don't seem to have the equation/sources any longer...


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
    population_2005 = get_population(bioregion)
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
    #get last of the wild ecoregions 
    wild_regions = get_last_wild(bioregion)
    #get marine ecregions
    marine_ecoregions = get_marine_ecoregions(bioregion)
    #get land mass proportion
    landmass_perc = get_landmass_proportion(area)
    #get npp proportion
    npp_perc = get_npp_proportion(bioregion)
    #get net primary production
    avg_npp = get_avg_npp(bioregion)
    #get soil suitability
    soil_suitability = get_soil_suitability(bioregion)    
    #compile context
    context = {'bioregion': bioregion, 'default_value': default_value, 'area': area, 'population_2005': population_2005, 'population_2015': population_2015, 'languages': languages, 'max_temp_c': max_temp_c, 'max_temp_f': max_temp_f, 'min_temp_c': min_temp_c, 'min_temp_f': min_temp_f, 'annual_temp_c': annual_temp_c, 'annual_temp_f': annual_temp_f, 'annual_temp_range_c': annual_temp_range_c, 'annual_temp_range_f': annual_temp_range_f, 'annual_precip': annual_precip, 'ecoregions': ecoregions, 'wild_regions': wild_regions, 'marine_ecoregions': marine_ecoregions, 'landmass_perc': landmass_perc, 'soil_suitability': soil_suitability, 'avg_npp': avg_npp, 'npp_perc': npp_perc}
    return context
    #get average poverty index
    #poverty = get_poverty(bioregion)
    #get soil moisture
    #soil_moisture = get_soil_moisture(bioregion)
    
           
def get_size(bioregion):
    area = int(round(geometry_area_in_display_units(bioregion.output_geom)))
    return area
           
def get_population(bioregion):
    #this may have changed to 2005 -- see Analisa and update ninkasi
    pop_geom = RasterDataset.objects.get(name='population_2005')
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
        languages = Languages.objects.filter(geometry__bboverlaps=bioregion.output_geom)
        language_dict = {}
        for language in languages:
            try:
                does_intersect = language.geometry.intersects(bioregion.output_geom)
                if does_intersect:
                    if language.nam_ansi is None:
                        name = 'Areas of No Data'
                    else:
                        name = language.nam_ansi
                    area = geometry_area_in_display_units(language.geometry.intersection(bioregion.output_geom))
                    if name in language_dict.keys():
                        language_dict[name] += area
                    else:
                        language_dict[name] = area
            except:
                #does_intersect = clean_geometry(language.geometry).intersects(bioregion.output_geom)
                pass
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
        ecoregion_tuples = get_report_cache(bioregion, 'ecoregions')
        return ecoregion_tuples
    else:
        ecoregions = EcoRegions.objects.filter(geometry__bboverlaps=bioregion.output_geom)
        ecoregion_tuples = [(ecoregion.geometry.intersection(bioregion.output_geom).area, ecoregion.eco_name) for ecoregion in ecoregions if ecoregion.geometry.intersects(bioregion.output_geom)]
        ecoregion_dict = {}
        for area,name in ecoregion_tuples:
            if name in ecoregion_dict.keys():
                ecoregion_dict[name] += area
            else:
                ecoregion_dict[name] = area
        ecoregion_tuples = [(name, convert_float_to_area_display_units(area)) for name,area in ecoregion_dict.items()]
        ecoregion_tuples.sort()
        #ecoregion_names = [name for (area, name) in ecoregion_tuples]
        create_report_cache(bioregion, dict(ecoregions=ecoregion_tuples))
        #just return the following for now (until we get caching in place)
        #ecoregion_names = ['Central and Southern Cascades forests', 'Central Pacific coastal forests', 'Willamette Valley forests', 'Puget lowland forests', 'Eastern Cascades forests', 'Klamath-Siskiyou forests', 'Snake-Columbia shrub steppe', 'Blue Mountains forests']
        return ecoregion_tuples    
    
def get_last_wild(bioregion):
    if report_cache_exists(bioregion, 'wild_regions'):
        lastwild_tuples = get_report_cache(bioregion, 'wild_regions')
        return lastwild_tuples
    else:
        wild_regions = LastWild.objects.filter(geometry__bboverlaps=bioregion.output_geom)
        wild_region_tuples = [(wild_region.geometry.intersection(bioregion.output_geom).area, wild_region.eco_name) for wild_region in wild_regions if wild_region.geometry.intersects(bioregion.output_geom)]
        wild_region_dict = {}
        for area,name in wild_region_tuples:
            if name is not None:
                if name in wild_region_dict.keys():
                    wild_region_dict[name] += area
                else:
                    wild_region_dict[name] = area
        wild_region_tuples = [(name, convert_float_to_area_display_units(area)) for name,area in wild_region_dict.items()]
        wild_region_tuples.sort()
        create_report_cache(bioregion, dict(wild_regions=wild_region_tuples))
        return wild_region_tuples  
    
def get_marine_ecoregions(bioregion):
    if report_cache_exists(bioregion, 'marineregions'):
        marineregion_tuples = get_report_cache(bioregion, 'marineregions')
        return marineregion_tuples
    else:
        marineregions = MarineRegions.objects.filter(geometry__bboverlaps=bioregion.output_geom)
        marineregion_tuples = [(marineregion.geometry.intersection(bioregion.output_geom).area, marineregion.ecoregion) for marineregion in marineregions if marineregion.geometry.intersects(bioregion.output_geom)]
        marineregion_dict = {}
        for area,name in marineregion_tuples:
            if name in marineregion_dict.keys():
                marineregion_dict[name] += area
            else:
                marineregion_dict[name] = area
        marineregion_tuples = [(name, convert_float_to_area_display_units(area)) for name,area in marineregion_dict.items()]
        marineregion_tuples.sort()
        create_report_cache(bioregion, dict(marineregions=marineregion_tuples))
        return marineregion_tuples    
    
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
