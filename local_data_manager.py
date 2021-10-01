# from shutil import rmtree
# from glob import glob
# import json
from pprint import pprint
# import os
# import pandas as pd
# import numpy as np
# import multiprocessing


# from modules.withMongo import post_collection
# from modules.withMRMS import Fetch, ProbSevere, render_tiles
# from modules.withFetch import Fetch
# from modules.useProcess import process_tiles, process_probsevere
from use.baseproducts import BaseProducts
# from use.probsevere import ProbSevere
# from pprint import pprint
import time


##############|  DEFAULT PATH   |#################
TMP_RAW = 'tmp/raw/'
TMP_IMG = 'tmp/img/'
TMP_DATA = 'tmp/data/'
directories = (TMP_RAW, TMP_IMG, TMP_DATA)


##############|  REGEX   |#################
RE_DATA = r"(?<=tmp/data/)(.*)"
GLB_DATA = TMP_DATA+'*/*/*/*/'


# def _write(data):
#     # only the probSevere JSON data is
#     # passed to this function.
#     post_collection(data, collection='PROBSEVERE')
#     for filename in glob(os.path.join(GLB_DATA, '*.png')):
#         with open(filename, 'rb') as tile:
#             post_collection(tile, collection='FILESERVER')
#     return

# rmtree('tmp/', ignore_errors=False, onerror=None)
# ps = ProbSevere()


def ldm_controller():
    """
    # Steps

    # collect:
        Opens baseProducts.json and pulls data from the MRMS Dataset using the Fetch module.

    # prep:
        prep itterates through the dataset and calls the aplicable functions to process the data.  Additional

    # process:
        calls modules to process the grib and json data.

    # write:
        stores the processed information into the mongodb database

    # manage:
        manage is called at the START and STOP.  manage

    """
    #####################|  PROBSEVERE INSTANCE   |#####################
    # First an EXSISTING instance of ProbSevere is passed into a NEW instance BaseProducts.
    #
    # BaseProducts manages its own state without resetting the ProbSevere state.
    #
    # ProbSevere returns GeoJson to BaseProducts which is then saved to MONGO DB
    # Each new instance of BaseProducts removes the existing GeoJSON from memory.
    # While ProbSevere maintains its memory outside of the loop for compairsons
    # to previous itteratings of ndarrays.
    #
    ########################################################

    bp = BaseProducts()
    # maintain_tmp_tree creates a new tmp tree dir for intermediate processing
    initial_timer = bp.maintain_tmp_tree('START')
    #####################|  COLLECT   |#####################
    # call the baseproducts fetch api to collect the raw data
    ########################################################
    intermediate_timer = time.time()
    bp.collect(save_loc=TMP_RAW)
    print(f'data collection accomplished in: \
            {round(time.time() - intermediate_timer)} seconds')

    ######################|  PREPARE & PROCESS  |#################
    # call the baseproducts prepare_and_process function.
    # this stage relies heavily on the withMRMS module and MMM-py
    # to handle the data processing required to render the png images.
    ###############################################################
    intermediate_timer = time.time()
    # bp.prepare_and_process(dtype='JSON')
    bp.prepare_and_process(dtype='GRIB2')
    print(f'data processing accomplished in: \
            {round(time.time() - intermediate_timer)} seconds')

    #######################|  COMMIT & POST   |####################
    #
    ###############################################################
    intermediate_timer = time.time()
    bp.commit_and_post()

    print(f'data writing took \
            {round(time.time() - intermediate_timer)} seconds')
    # pprint(ps.feature_collection)
    # once the database is updated maintain_tmp_tree then removes tmp/ and all associated files.
    end_timer = bp.maintain_tmp_tree('STOP')
    print(f'total processing accomplished in: \
            {round(end_timer - initial_timer)} seconds')


# with open('tmp/raw/MRMS_PROBSEVERE_20210928_111041.json', 'r') as f:
#     json_object = json.load(f)
#     print(json_object['validTime'],json_object['features'])


ldm_controller()
