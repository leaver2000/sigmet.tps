from pprint import pprint
import json
import pandas as pd
import numpy as np
FEATURE_COLLECTION = dict(version='3.0.1', type='FeatureCollection',
                          product='ProbSevere', source="NOAA/NCEP Central Operations")

GEOMETRY_COLLECTION = dict(type="GeometryCollection")


def enumerater_collection(arr):
    features = list()
    # for index, value in enumerate(arr):
    for value in arr:
        features.append(handle_feature(value[6]))
    return features


def get_storm_motion(mtn_s, mtn_e, mean_w):
    return [mtn_s, mtn_e, mean_w]


def handle_feature(feat):
    # PROPS
    geom = feat['geometry']
    props = feat['properties']
    props['MODELS'] = feat['models']['probsevere']['LINE01']
    # CRDS
    crds = geom['coordinates']
    lons, lats = np.rollaxis(np.array(crds), 2, 0)
    geometries = list()
    geometries.append(geom)
    geometries.append(dict(type="point", coordinates=[
                      np.mean(lons), np.mean(lats)]))

    geometries.append(dict(type="MultiLineString", coordinates=get_storm_motion(
        props['MOTION_SOUTH'], props['MOTION_EAST'], props['MEANWIND_1-3kmAGL'])))
    # geom['track'] = get_storm_motion(
    #     props['MOTION_SOUTH'], props['MOTION_EAST'], props['MEANWIND_1-3kmAGL'])

    del feat['geometry']
    feat['geometry'] = dict(type="GeometryCollection", geometries=geometries)

    del feat['models']
    return feat


def use_feature(file=None, collection=None):
    with open(file, 'rb') as prob_severe:
        feature_collection = np.array(pd.read_json(prob_severe))
        validtime = feature_collection[0][2]
        features = enumerater_collection(feature_collection)
        collection['validtime'] = validtime
        collection['features'] = features
    return collection


b = use_feature('data/MRMS_PROBSEVERE_20210925_144634.json',
                collection=FEATURE_COLLECTION)


pprint(b['features'][0]['geometry'])


# "geometry": {
#   "type": "GeometryCollection",
#   "geometries": [
#     {
#       "type": "Point",
#       "coordinates": [61.34765625,48.63290858589535]
#     },
#     {
#       "type":"MultiLineString",
#       "coordinates":[
#         [[10,20],[10,20]],
#         [[10,20],[10,20]],
#         [[10,20],[10,20]]
#       ]
#     },
#     {
#       "type": "Polygon",
#       "coordinates":[[[-84.31,29.14],[-84.27,29.13],[-84.26,29.11],[-84.26,29.07],[-84.27,29.05],[-84.30,29.05],[-84.33,29.07],[-84.33,29.12],[-84.31,29.14]]]
#     }]
