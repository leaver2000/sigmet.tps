import numpy as np
# from pprint import pprint
VERSION='3.0.1'
TYPE='FeatureCollection'
PRODUCT="probSevere:vectors"
SOURCE="NOAA/NCEP Central Operations"

class StormTrackVector:
    _stv={}
    def set_vector(self, _id=None,center=None, motion_east=None, motion_south=None ):
        self._id=_id
        self._center=center
        me = float(motion_east)
        mn = np.multiply(float(motion_south), -1)
        self.motion = np.array([me, mn])
        slope = np.divide(mn,me)

        if _id in self._stv.keys():
            pass
        else:
            self._stv[_id]={
                "motion":self.motion,
                "center":center,
                "slope":slope,
                "vector_space":self._space()
            }

    def _offsets(self):
        offsettime = [900,1800,2700,3600]#m/s offset for 2,15,30,45,60
        return[np.multiply(self.motion, x) for x in offsettime]


    def _space(self):
        lat,lon = self._center 
        arr = []
        R = 6378137
        for dn, de in self._offsets():
            # Coordinate offsets in radians
            dLat = dn/R
            radLat = np.multiply(np.pi, lat/180)  # np.pi*lat/180
            dLon = de/(R*np.cos(radLat))
            # OffsetPosition, decimal degrees
            latO = lat + dLat * 180/np.pi
            lonO = lon + dLon * 180/np.pi
            arr.append([latO, lonO])
        return arr

    def _multi_line_string(self):
        mls = self._stv[self._id]
        return [mls['vector_space']]


stv = StormTrackVector()
class ProbSevere:
    """
    The probsevere class maintains a persitance instance on the sever and accepts no __init__ fn arguments.

    usage:

    ps = ProbSevere()
    with open('MRMS_PROBSEVERE.json', 'r') as f:
        fc = json.load(f)
        ps.set(valid_time=fc['validTime'], features=fc['features'])


    """
    def __init__(self, valid_time=None, features=None):
        _features = []
        self.feature_collection={
            'version':VERSION,
            'type':TYPE,
            'validtime':valid_time,
            'product':PRODUCT,
            'source':SOURCE,
            'features':_features,
        }
        for feat in features:
            _features.append(self._reduce(feat))
        return

    def _reduce(self, feat):
        # PROPS
        geom = feat['geometry']
        props = feat['properties']
        props['MODELS'] = feat['models']['probsevere']['LINE01']
        # CRDS
        crds = geom['coordinates']
        lons, lats = np.rollaxis(np.array(crds), 2, 0)
        geometries = []
        geometries.append(geom)

        ################################|   MEAN CENTER    |############################################
        center = [np.mean(lons), np.mean(lats)]
        geometries.append({
            'type':'point',
            'coordinates':center
        })
        
        ################################|   MultiLineString    |############################################
        storm_id = props['ID']
        mtn_s = props['MOTION_SOUTH']
        mtn_e = props['MOTION_EAST']
        stv.set_vector(_id=storm_id, motion_east=mtn_e, motion_south=mtn_s,center=center)
        mls = stv._multi_line_string()
        ssts= {
            'type':'MultiLineString',
            'coordinates':mls
        }

        geometries.append(ssts)

        ################################|   PROB SEVERE POLLYGON    |############################################
        feat['geometry'] ={
            'geometries':geometries
        }
        del feat['models']
        return feat




# def linear_track(crds):
#     return crds


# def parametrization_track(crds):
#     return crds


# def get_storm_motion(mtn_s, mtn_e, mean_w):
#     lt = linear_track([mtn_s, mtn_e, mean_w])
#     pt = parametrization_track([mtn_s, mtn_e, mean_w])
#     return [lt, pt]



