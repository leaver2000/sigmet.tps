from pprint import pprint
import json
import pandas as pd
import numpy as np
FEATURE_COLLECTION = dict(version='3.0.1',type='FeatureCollection',product='ProbSevere',source="NOAA/NCEP Central Operations")


def enumerater_collection(arr):
    features = list()
    # for index, value in enumerate(arr):
    for value in arr:
        features.append(handle_feature(value[6]))
    return features


def get_storm_motion(mtn_s,mtn_e,mean_w):
    return [mtn_s,mtn_e,mean_w]


def handle_feature(feat):
    #PROPS
    geom = feat['geometry']
    props = feat['properties']
    props['MODELS'] = feat['models']['probsevere']['LINE01']  
    # CRDS
    crds = geom['coordinates']
    lons,lats = np.rollaxis(np.array(crds),2,0)
    geom['centroid'] = [np.mean(lons),np.mean(lats)]
    geom['track']=get_storm_motion(props['MOTION_SOUTH'],props['MOTION_EAST'],props['MEANWIND_1-3kmAGL'])
    del feat['models']
    return feat



# with open('tmp/raw/MRMS_PROBSEVERE_20210926_053837.json', 'rb') as prob_severe:
#     feature_collection = np.array(pd.read_json(prob_severe))
#     validtime = feature_collection[0][2]
#     features = enumerater_collection(feature_collection)
#     FEATURE_COLLECTION['validtime']=validtime
#     FEATURE_COLLECTION['features']=features
#     pprint(FEATURE_COLLECTION)

def use_feature(file=None,collection=None):
    with open(file, 'rb') as prob_severe:
        feature_collection = np.array(pd.read_json(prob_severe))
        validtime = feature_collection[0][2]
        features = enumerater_collection(feature_collection)
        collection['validtime']=validtime
        collection['features']=features
    return collection
        # pprint(FEATURE_COLLECTION)    
    # pprint(dict(validtime=validtime,features=features))
b= use_feature('tmp/raw/MRMS_PROBSEVERE_20210926_053837.json',collection=FEATURE_COLLECTION)
pprint(b)
# st = 'ProbHail: 0%; ProbWind: 1%; ProbTor: 0%'
# obj = np.array(st,dtype=object)
# print(np.array(st,dtype=object))
# print(type(obj), len(obj))
# print(pd.Series.to_json(st))