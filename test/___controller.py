from dps.baseproducts import BaseProducts
from dps.router import Router
from dps.env import ld
import time
import os
from glob import glob


def controller(verbose=False):
    """
    # Steps

    # collect:
        Opens baseProducts.json and pulls data from the MRMS Dataset using the Fetch module.

    # prep:
        prep itterates through the dataset and calls the aplicable functions to process the data.  Additional

    # post:

    # update

    """
    #*####################|  PROBSEVERE INSTANCE   |#####################
    # First an EXSISTING instance of ProbSevere is passed into a NEW instance BaseProducts.
    #
    # BaseProducts manages its own state without resetting the ProbSevere state.
    #
    # ProbSevere returns GeoJson to BaseProducts which is then saved to MONGO DB
    # Each new instance of BaseProducts removes the existing GeoJSON from memory.
    # While ProbSevere maintains its memory outside of the loop for compairsons
    # to previous itteratings of ndarrays.
    #
    #*#######################################################

    bp = BaseProducts()
    # maintain_tmp_tree creates a new tmp tree dir for intermediate processing
    initial_timer = ld.manage('START')
    #####################|  COLLECT   |#####################
    # call the baseproducts fetch api to collect the raw data
    ########################################################
    if verbose:
        intermediate_timer = time.time()

    bp.collect()

    if verbose:
        print(f'data collection accomplished in: \n\
                {round(time.time() - intermediate_timer)} seconds')

    ######################|  PREPARE & PROCESS  |#################
    # call the baseproducts prepare_and_process function.
    # this stage relies heavily on the withMRMS module and MMM-py
    # to handle the data processing required to render the png images.
    ###############################################################
        intermediate_timer = time.time()
        print('processing raw MRMS data')

    bp.process()

    if verbose:
        print(f'data processing accomplished in: \
                {round(time.time() - intermediate_timer)} seconds')

        intermediate_timer = time.time()
    #######################|  COMMIT & POST   |####################
    #
    ###############################################################

    # print(bp.fileservice)
    route = Router()
    route.probsevere(bp.probsevere)
    # print(glob(os.path.join('tmp/data/*/*/*/*/', '*.png')))
    route.gridfs(glob(os.path.join('tmp/data/*/*/*/*/', '*.png')))
    route.done(bp.features)

    if verbose:
        print(f'data writing took \
                {round(time.time() - intermediate_timer)} seconds')

    # * once the database is updated maintain_tmp_tree then removes tmp/ and all associated files.
    end_timer = ld.manage('STOP')
    if verbose:
        print(f'total processing accomplished in: \
                {round(end_timer - initial_timer)} seconds')

    return None
