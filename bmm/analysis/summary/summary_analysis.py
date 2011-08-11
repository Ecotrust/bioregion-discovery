#from django.http import HttpResponse
from django.shortcuts import render_to_response#, get_object_or_404
from django.template import RequestContext
from lingcod.raster_stats.models import RasterDataset, zonal_stats
#from analysis.models import *
#from settings import *
from lingcod.unit_converter.models import geometry_area_in_display_units, convert_float_to_area_display_units
from analysis.utils import convert_sq_km_to_sq_mi, convert_cm_to_in, get_terra_geom, get_oceanic_geom
from analysis.models import Languages, EcoRegions, LastWild, MarineRegions, Watersheds, WorldMask
from analysis.caching.report_caching import *
from lingcod.common.utils import clean_geometry

default_value = '---'
global_landmass = 148940000. #sq km -- see table at http://en.wikipedia.org/wiki/Earth
global_area = 510072000. #sq km -- see table at http://en.wikipedia.org/wiki/Earth
#npp_grid_cell_size = 676000000. #sq m -- approximated via measurement tool in arcmap 
#npp_grid_cell_size = 16684.47387 * 16684.47387
#global_npp = 62000000000000000 #need to re-figure this value (don't seem to have the equation/sources any longer...
avg_terrestrial_npp = 426
avg_oceanic_npp = 140 


'''
Runs analysis for Summary report
Called by analysis.views.summary_analysis
'''
def display_summary_analysis(request, bioregion, template='summary_report.html'):
    context = run_summary_analysis(bioregion)
    return render_to_response(template, RequestContext(request, context)) 
     
def display_general_analysis(request, bioregion, template='summary/general_report.html'):
    #get size of bioregion
    area_km, area_mi = get_size(bioregion.output_geom)
    #get terrestrial area
    terra_area_km, terra_area_mi = get_terra_area(bioregion)
    #get oceanic area
    oceanic_area_km, oceanic_area_mi = get_oceanic_area(bioregion)
    #get current population (for 2010)
    population_2005 = get_population(bioregion)
    #get projected population (for 2015)
    population_2015 = get_projected_population(bioregion)
    #get median max temperature
    max_temp_c, max_temp_f = get_max_temp(bioregion)
    #get median min temperature
    min_temp_c, min_temp_f = get_min_temp(bioregion)
    #get mean annual temperature
    annual_temp_c, annual_temp_f = get_annual_temp(bioregion)
    #get mean annual temperature range
    annual_temp_range_c = max_temp_c - min_temp_c
    annual_temp_range_f = max_temp_f - min_temp_f
    #get mean annual precipitation
    annual_precip_cm, annual_precip_in = get_annual_precip(bioregion)
    context = {'bioregion': bioregion, 'default_value': default_value, 'area_km': area_km, 'area_mi': area_mi, 'terra_area_km': terra_area_km, 'terra_area_mi': terra_area_mi, 'oceanic_area_km': oceanic_area_km, 'oceanic_area_mi': oceanic_area_mi, 'population_2005': population_2005, 'population_2015': population_2015, 'max_temp_c': max_temp_c, 'max_temp_f': max_temp_f, 'min_temp_c': min_temp_c, 'min_temp_f': min_temp_f, 'annual_temp_c': annual_temp_c, 'annual_temp_f': annual_temp_f, 'annual_temp_range_c': annual_temp_range_c, 'annual_temp_range_f': annual_temp_range_f, 'annual_precip_cm': annual_precip_cm, 'annual_precip_in': annual_precip_in}
    return render_to_response(template, RequestContext(request, context)) 
     
def display_language_analysis(request, bioregion, template='summary/language_report.html'):
    #get list of spoken languages
    languages = get_languages(bioregion)
    context = {'bioregion': bioregion, 'default_value': default_value, 'languages': languages}
    return render_to_response(template, RequestContext(request, context)) 
    
def display_resources_analysis(request, bioregion, template='summary/resources_report.html'):
    #get net primary production
    terr_npp_avg = get_terr_npp_avg(bioregion)
    ocn_npp_avg = get_ocn_npp_avg(bioregion)
    #get soil suitability
    soil_suitability = get_soil_suitability(bioregion) 
    #get equipped for irrigation proportion
    equipped_for_irrigation = get_proportion_equipped_for_irrigation(bioregion)
    #get watersheds
    watersheds = get_watersheds(bioregion)
    #get existing eco-regions
    ecoregions = get_ecoregions(bioregion)
    #get last of the wild ecoregions 
    wild_regions = get_last_wild(bioregion)
    #get marine ecregions
    marine_ecoregions = get_marine_ecoregions(bioregion)
    context = {'bioregion': bioregion, 'default_value': default_value, 'watersheds': watersheds, 'ecoregions': ecoregions, 'wild_regions': wild_regions, 'marine_ecoregions': marine_ecoregions, 'terr_npp_avg': terr_npp_avg, 'ocn_npp_avg': ocn_npp_avg, 'avg_terrestrial_npp': avg_terrestrial_npp, 'avg_oceanic_npp': avg_oceanic_npp, 'soil_suitability': soil_suitability, 'equipped_for_irrigation': equipped_for_irrigation}
    return render_to_response(template, RequestContext(request, context)) 
'''    
def display_agriculture_analysis(request, bioregion, template='summary/agriculture_report.html'):
    #get soil suitability
    soil_suitability = get_soil_suitability(bioregion) 
    #get equipped for irrigation proportion
    equipped_for_irrigation = get_proportion_equipped_for_irrigation(bioregion)
    context = {'bioregion': bioregion, 'default_value': default_value, 'soil_suitability': soil_suitability, 'equipped_for_irrigation': equipped_for_irrigation}
    return render_to_response(template, RequestContext(request, context)) 
'''
def get_size(geom):
    area_km = int(round(geometry_area_in_display_units(geom)))
    area_mi = int(round(convert_sq_km_to_sq_mi(area_km)))
    return area_km, area_mi
    
def get_terra_area(bioregion):
    terra_geom = get_terra_geom(bioregion)
    terra_area_km = int(round(geometry_area_in_display_units(terra_geom)))        
    terra_area_mi = int(round(convert_sq_km_to_sq_mi(terra_area_km)))
    return terra_area_km, terra_area_mi    
    
def get_oceanic_area(bioregion):
    oceanic_geom = get_oceanic_geom(bioregion)
    oceanic_area_km = int(round(geometry_area_in_display_units(oceanic_geom)))
    oceanic_area_mi = int(round(convert_sq_km_to_sq_mi(oceanic_area_km)))
    return oceanic_area_km, oceanic_area_mi  

def get_population(bioregion):
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
    
def get_annual_precip(bioregion):
    precip_geom = RasterDataset.objects.get(name='annual_precipitation')
    precip_stats = zonal_stats(bioregion.output_geom, precip_geom)
    precip_cm = precip_stats.avg / 10
    precip_in = convert_cm_to_in(precip_cm)
    return precip_cm, precip_in
    
def get_watersheds(bioregion):
    if report_cache_exists(bioregion, 'watersheds'):
        watershed_tuples = get_report_cache(bioregion, 'watersheds')
        return watershed_tuples
    else:
        watersheds = Watersheds.objects.filter(geometry__bboverlaps=bioregion.output_geom)
        watershed_tuples = [(watershed.geometry.intersection(bioregion.output_geom).area, watershed.maj_name) for watershed in watersheds if watershed.geometry.intersects(bioregion.output_geom)]
        watershed_dict = {}
        for area,name in watershed_tuples:
            if name in watershed_dict.keys():
                watershed_dict[name] += area
            else:
                watershed_dict[name] = area
        watershed_tuples = [(name, convert_float_to_area_display_units(area)) for name,area in watershed_dict.items()]
        watershed_tuples.sort()
        watershed_tuples = [(watershed_tuple[0], watershed_tuple[1], convert_sq_km_to_sq_mi(watershed_tuple[1])) for watershed_tuple in watershed_tuples]
        create_report_cache(bioregion, dict(watersheds=watershed_tuples))
        return watershed_tuples    
    
    
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
        ecoregion_tuples = [(eco_tuple[0], eco_tuple[1], convert_sq_km_to_sq_mi(eco_tuple[1])) for eco_tuple in ecoregion_tuples]
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
        wild_region_tuples = [(wild_tuple[0], wild_tuple[1], convert_sq_km_to_sq_mi(wild_tuple[1])) for wild_tuple in wild_region_tuples]
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
        marineregion_tuples = [(marine_tuple[0], marine_tuple[1], convert_sq_km_to_sq_mi(marine_tuple[1])) for marine_tuple in marineregion_tuples]
        create_report_cache(bioregion, dict(marineregions=marineregion_tuples))
        return marineregion_tuples    
    
def get_global_area_proportion(area_km):
    perc = area_km / global_area
    return perc   
    
def get_landmass_proportion(area):
    perc = area / global_landmass
    return perc
    
def get_soil_suitability(bioregion):
    terra_geom = get_terra_geom(bioregion)
    suit_geom = RasterDataset.objects.get(name='soil_suitability')
    suit_stats = zonal_stats(terra_geom, suit_geom)
    proportion = suit_stats.avg
    area_km, area_mi = get_size(terra_geom)
    prop_area_km = area_km * proportion
    prop_area_mi = area_mi * proportion
    return (proportion, prop_area_km, prop_area_mi)

def get_proportion_equipped_for_irrigation(bioregion):
    terra_geom = get_terra_geom(bioregion)
    irrig_geom = RasterDataset.objects.get(name='irrig_equipped')
    irrig_stats = zonal_stats(terra_geom, irrig_geom)
    hectares = irrig_stats.sum
    area_km, area_mi = get_size(terra_geom)
    proportion = hectares / 100 / area_km
    prop_area_km = area_km * proportion
    prop_area_mi = area_mi * proportion
    return (proportion, prop_area_km, prop_area_mi)
    
def get_terr_npp_avg(bioregion):
    terra_geom = get_terra_geom(bioregion)
    npp_geom = RasterDataset.objects.get(name='npp_terr')
    npp_stats = zonal_stats(terra_geom, npp_geom)
    npp_avg = npp_stats.avg / (26064.03459 ** 2)
    return npp_avg

def get_ocn_npp_avg(bioregion):
    oceanic_geom = get_oceanic_geom(bioregion)
    if oceanic_geom.area == 0:
        npp_avg = 0
    else:
        npp_geom = RasterDataset.objects.get(name='npp_ocn')
        #settling on the following to account for lack of overlap
        #(see if statement above which helps with this issue as well)
        try:
            npp_avg = npp_stats.avg * 365 / 1000 #mg per day converted to g per year
        except:
            npp_avg = 0
    return npp_avg
    
def get_poverty(bioregion):
    return default_value
    poverty_geom = RasterDataset.objects.get(name='poverty')
    poverty_stats = zonal_stats(bioregion.output_geom, poverty_geom)
    return poverty_stats.avg
