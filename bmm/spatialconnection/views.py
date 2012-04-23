# Create your views here.
from django.http import Http404
from django.shortcuts import render_to_response#, get_object_or_404
from django.template import RequestContext
from mybioregions.models import MyBioregion, DrawnBioregion, StoryPoint
from madrona.features import get_feature_by_uid

def storyconnect(request, uid):
    try:
        feature = get_feature_by_uid(uid) 
    except:
        raise Http404('UID %s does not exist' % uid)

    fgeom = feature.output_geom
    if not fgeom.valid:
        fgeom = fgeom.buffer(0)
 
    hits = []

    for s in StoryPoint.objects.filter(geometry_final__bboverlaps=fgeom):
        sgeom = s.geometry_final
        if sgeom.intersects(fgeom):
            hits.append(s)

    context = {
        'hits': hits,
    }
    return render_to_response('storyconnect.html', RequestContext(request, context)) 

def bioconnect(request, uid):
    try:
        feature = get_feature_by_uid(uid) 
    except:
        raise Http404('UID %s does not exist' % uid)

    fgeom = feature.output_geom
    if not fgeom.valid:
        fgeom = fgeom.buffer(0)
 
    hits = []

    for mb in MyBioregion.objects.filter(output_geom__bboverlaps=fgeom):
        mbgeom = mb.output_geom
        if not mbgeom.valid:
            mbgeom = mbgeom.buffer(0)
        if mbgeom.intersects(fgeom):
            hits.append(mb)

    for d in DrawnBioregion.objects.filter(geometry_final__bboverlaps=fgeom):
        dgeom = d.output_geom
        if not dgeom.valid:
            dgeom = dgeom.buffer(0)
        if dgeom.intersects(fgeom):
            hits.append(d)

    context = {
        'hits': hits,
    }
    return render_to_response('bioconnect.html', RequestContext(request, context)) 
