from django.core.management import setup_environ
import os
import sys
sys.path.append(os.path.dirname(__file__))

import settings
setup_environ(settings)

#==================================#
from mybioregions.models import *
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.auth.models import User, Group
from lingcod.analysistools.grass import Grass
from lingcod.analysistools.utils import linear_regression
import random

lines = open("../data/cities15000.txt").readlines()
user = User.objects.get(username='demo')

def get_random_city():
    line = random.choice(lines)
    data = line.strip().split('\t')
    return float(data[5]), float(data[4]), data[1]

def delete(): 
    for model in [MyBioregion, Folder]:
        a = model.objects.filter(user=user)
        for i in a:
            i.delete()

def main():
    user = User.objects.get(username='demo')

    for i in range(200):
        x,y,name = get_random_city()
        g = GEOSGeometry('SRID=4326;POINT(%s %s)' % (x,y))
        print "# ", i, " #######", g

        desired_size = random.choice(SIZE_LOOKUP.keys())
        desired_size_mHa = SIZE_LOOKUP[desired_size]
        marine = 0
        if random.choice([True,False]):
            marine = random.randrange(0,100)
        bio = MyBioregion(user=user, name=name, 
                input_temp_weight = random.randrange(0,100),
                input_precip_weight = random.randrange(0,100),
                input_biomass_weight = random.randrange(0,100),
                input_lang_weight = random.randrange(0,100),
                input_elev_weight = random.randrange(0,100),
                input_marine_weight = marine, 
                input_starting_point = g,
                input_bioregion_size= desired_size
                ) 
        bio.save()
        try:
            ratio = (bio.output_geom.area/10000000000.0) / desired_size_mHa
            if ratio < 0.001:
                bio.delete()
        except:
            pass
        del bio

def summary():
    print "name","numruns","finalcost","sumweights","size","output_area", "sum*area"
    knowns = []
    costs = []
    init = []
    final = []
    numruns = []
    diff = []
    for bio in MyBioregion.objects.filter(user=user):
        if not bio.output_geom:
            continue
        sumw = (bio.input_biomass_weight + bio.input_precip_weight + bio.input_biomass_weight)
        mHa = bio.output_geom.area/10000000000.0
        known = sumw * (mHa ** 0.5)
        cost = bio.output_finalcost
        desired_size_mHa = SIZE_LOOKUP[bio.input_bioregion_size]
        ratio = mHa / desired_size_mHa
        if ratio > 0.8 and ratio < 1.2 and cost < 500000000:
            knowns.append(known)
            costs.append(cost)
            init.append(bio.output_initcost)
            final.append(bio.output_finalcost)
            try: 
                dif = bio.output_initcost - bio.output_finalcost
            except:
                dif = None
            diff.append(dif)
            numruns.append(bio.output_numruns)
            print bio.name, bio.output_numruns, "   ", int(bio.output_finalcost), "   ", sumw, \
                bio.input_bioregion_size, mHa, known, ratio

    import matplotlib.pyplot as plt
    print 
    print knowns
    print costs
    print
    a,b,r2 = linear_regression(knowns,costs)
    print "cost = %s(multweights*size_in_mHa) + %s" % (a,b)
    print " n = ", len(knowns)
    print " R^2 =", r2
    print
    #plt.subplot(211)
    plt.scatter(knowns, costs)

    print min(costs)
    print max(costs)
    #b = 0
    def calc(x):
        return a * x + b 
    linexs = [0, max(knowns)]
    lineys = [calc(x) for x in linexs]
    #plt.subplot(212)
    plt.plot(linexs, lineys)
    #plt.scatter(init, final)
    #plt.hist(diff)
    plt.show()


if __name__ == '__main__':
    delete()
    main()
    summary()
