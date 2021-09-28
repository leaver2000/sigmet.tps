import numpy as np

#####################|      inital     |###########################################
# props = np.array(['validtime', 'crds', '...props'])
# lv = np.array(['linear_vector'])
# pt = np.array(['parametrization_of_the_curve'])
# lrm = np.array(['linear_regression_model'])
# prm = np.array(['polynomial_regression_model'])
# plots = np.array([props, lv, pt, lrm, prm])
# spaghetti_plots = np.array(['storm_id', plots])
# print(spaghetti_plots.shape)


class StormTrack:
    """
    # StormTrack model for the MRMS ProbSevere algorithm

    for a given instance storm tracks are bucketed and accessable via spaghetti_plots.

    data is stored in a numpy array()


    array([array(['validtime', 'crds', '...props'], dtype='<U9'),

            array(['linear_vector'], dtype='<U13'),

            array(['parametrization_of_the_curve'], dtype='<U28'),

            array(['linear_regression_model'], dtype='<U23'),

            array(['polynomial_regression_model'], dtype='<U27')], dtype=object)]


    linear_vector: storm track

    parametrization of the curve

    ML
    linear regression model
    polynomial regression model



    """
    spaghetti_plots = list()

    def set_motion(self, storm_id=None, motion_east=None, motion_south=None, wnd=None, crds=None):

        lt = self._linear([motion_east, motion_south])
        pt = self._parametrization([motion_east, motion_south])
        self.spaghetti_plots.append(np.array([storm_id, lt, pt], dtype=object))
        # print(lt, pt)
        return [lt, pt]

    def get_motion():
        return

    def _linear(self, crds):
        return crds

    def _parametrization(self, crds):
        return crds

    def _linear_regression():
        pass

    def _polynomial_regression():
        pass

    # def get_storm_motion(mtn_s, mtn_e, mean_w):
    #     lt = linear_track([mtn_s, mtn_e, mean_w])
    #     pt = parametrization_track([mtn_s, mtn_e, mean_w])
    #     return [lt, pt]
