from analysis.models import ReportCache

'''
Checks to see if cache for a given report exists in ReportCache table
'''
def report_cache_exists(bioregion, report):
    try:
        cache = ReportCache.objects.get(wkt_hash=bioregion.hash)
        if report in cache.context.keys():
            return True
        else:
            return False
    except:
        return False

'''
Retrieves cache for a given report exists in ReportCache table
'''
def get_report_cache(bioregion, report):
    try:
        cache = ReportCache.objects.get(wkt_hash=bioregion.hash)
        return cache.context[report]
    except:
        from django.core.exceptions import ObjectDoesNotExist
        raise ObjectDoesNotExist("Cache object (or context key) not found:  make sure report_cache_exists() is called prior to calling get_report_cache()")
    
    
'''
Creates and saves a cache entry for a given report in ReportCache table
'''
def create_report_cache(bioregion, context):
    #first check to see if cache exists, but context does not
    try:
        cache = ReportCache.objects.get(wkt_hash=bioregion.hash)
        for key,value in context.items():
            cache.context[key] = value
        cache.save()
    except:
        cache = ReportCache()
        cache.wkt_hash = bioregion.hash
        cache.context = context
        cache.save()
    
'''
Remove a single geometry from the cache table
'''    
def remove_report_cache(bioregion=None):
    if bioregion is None:
        raise Exception("For clearing all cached data, use clear_report_cache instead.")
    entries = ReportCache.objects.filter(wkt_hash=bioregion.hash)
    #remove entries from ReportCache
    for entry in entries:
        ReportCache.delete(entry)
       
'''
Clear all entries from cache table
'''    
def clear_report_cache(i_am_sure=False):
    if not i_am_sure:
        raise Exception("I don't believe you really want to do this...convince me.")
    entries = ReportCache.objects.all()
    for entry in entries:
        ReportCache.delete(entry)
        
