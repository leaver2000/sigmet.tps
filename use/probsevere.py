import numpy as np
from use.stormtrack import StormTrack
stormy = StormTrack()


class ProbSevere:
    """
    The probsevere class maintains a persitance instance on the sever and accepts no __init__ fn arguments.

    usage:

    ps = ProbSevere()
    with open('MRMS_PROBSEVERE.json', 'r') as f:
        fc = json.load(f)
        ps.set(valid_time=fc['validTime'], features=fc['features'])


    """

    def set_features(self, valid_time=None, features=None):
        _features = list()
        self.feature_collection = dict(version='3.0.1', type='FeatureCollection', validtime=valid_time, features=_features,
                                       product='ProbSevere:track', source="NOAA/NCEP Central Operations")
        for feat in features:
            _features.append(self._reduced_json(feat))

        return

    def _reduced_json(self, feat):
        # PROPS
        geom = feat['geometry']
        props = feat['properties']
        props['MODELS'] = feat['models']['probsevere']['LINE01']
        # CRDS
        crds = geom['coordinates']
        lons, lats = np.rollaxis(np.array(crds), 2, 0)
        geometries = list()
        geometries.append(geom)

        ################################|   CENTROID    |############################################
        centroid = dict(type="point", coordinates=[
                        np.mean(lons), np.mean(lats)])
        geometries.append(centroid)

        ################################|   SpaghettiStormTracks    |############################################
        storm_id = props['ID']
        mtn_s = props['MOTION_SOUTH']
        mtn_e = props['MOTION_EAST']
        wnd = props['MEANWIND_1-3kmAGL']
        storm_tracks = stormy.set_motion(
            storm_id=storm_id, motion_east=mtn_e, motion_south=mtn_s, wnd=wnd, crds=[lons, lats])
        # print(spaghetti_tracks)
        ssts = dict(type="MultiLineString",
                    name="SpaghettiStormTracks", coordinates=storm_tracks)
        geometries.append(ssts)

        ################################|   PROB SEVERE POLLYGON    |############################################

        del feat['geometry']
        feat['geometry'] = dict(
            type="GeometryCollection", geometries=geometries)

        del feat['models']
        return feat

    def list_np_plots(self):
        return stormy.spaghetti_plots

    # def _reduce(self, feat):
    #     pass

    # def _iterate(self, arr):
    #     for value in arr:
    #         # print(value)
    #         self.features.append(handle_feature(value[6]))


def linear_track(crds):
    return crds


def parametrization_track(crds):
    return crds


def get_storm_motion(mtn_s, mtn_e, mean_w):
    lt = linear_track([mtn_s, mtn_e, mean_w])
    pt = parametrization_track([mtn_s, mtn_e, mean_w])
    return [lt, pt]


# def reduce_feature(feat):
#     # PROPS
#     geom = feat['geometry']
#     props = feat['properties']
#     props['MODELS'] = feat['models']['probsevere']['LINE01']
#     # CRDS
#     crds = geom['coordinates']
#     lons, lats = np.rollaxis(np.array(crds), 2, 0)
#     geometries = list()
#     geometries.append(geom)

#     ################################|   CENTROID    |############################################
#     centroid = dict(type="point", coordinates=[np.mean(lons), np.mean(lats)])
#     geometries.append(centroid)

#     ################################|   STORM MOTION    |############################################
#     # storm_id = props['ID']
#     # mtn_s = props['MOTION_SOUTH']
#     # mtn_e = props['MOTION_EAST']
#     # wnd = props['MEANWIND_1-3kmAGL']
#     # storm_motion = stormy.set_motion(
#     #     storm_id=storm_id, motion_east=mtn_e, motion_south=mtn_s, wnd=wnd, crds=[lons, lats])
#     # geometries.append(dict(type="MultiLineString",name="SpaghettiStormTrack" coordinates=storm_motion))

#     ################################|   PROB SEVERE POLLYGON    |############################################
#     # geom['track'] = get_storm_motion(
#     #     props['MOTION_SOUTH'], props['MOTION_EAST'], props['MEANWIND_1-3kmAGL'])

#     del feat['geometry']
#     feat['geometry'] = dict(type="GeometryCollection", geometries=geometries)

#     del feat['models']
#     return feat
