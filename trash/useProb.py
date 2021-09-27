import numpy as np


class ProbSevere:
    def __init__(self, feature_collection=None):
        if feature_collection is not None:
            instance = feature_collection[0]
            validtime = instance[2]

            self.features = list()

            self.feature_collection = dict(version='3.0.1', type='FeatureCollection', validtime=validtime, features=self.features,
                                           product='ProbSevere:track', source="NOAA/NCEP Central Operations")

            self.geometry_collection = dict(type="GeometryCollection")

            self._iterate(feature_collection)

            return
        else:
            pass
        return None

    def _iterate(self, arr):
        for value in arr:
            # print(value)
            self.features.append(handle_feature(value[6]))


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
