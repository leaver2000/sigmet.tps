from shutil import rmtree
from glob import glob
import json
import os
import pandas as pd
import numpy as np
# import multiprocessing

# import pandas as pd
# import numpy as np

# from modules.useProb import ProbSevere
from modules.withMongo import post_collection, update_availiable_products
# from modules.withMRMS import Fetch, ProbSevere, render_tiles
from modules.useCollect import Fetch
from modules.useProcess import process_tiles, process_probsevere


# from pprint import pprint
import time


#######

##############|  DEFAULT PATH   |#################
TMP_RAW = 'tmp/raw/'
TMP_IMG = 'tmp/img/'
TMP_DATA = 'tmp/data/'
directories = (TMP_RAW, TMP_IMG, TMP_DATA)
REQUEST = 'request.json'
BASE_PRODUCTS = 'base_products.json'


##############|  REGEX   |#################
RE_DATA = r"(?<=tmp/data/)(.*)"
GLB_DATA = TMP_DATA+'*/*/*/*/'


def _write(data):
    # only the probSevere JSON data is
    # passed to this function.
    post_collection(data, collection='PROBSEVERE')
    for filename in glob(os.path.join(GLB_DATA, '*.png')):
        with open(filename, 'rb') as tile:
            post_collection(tile, collection='FILESERVER')
    return


def _prep(products):
    """
    Once the data is collected, it then enters the data preparation stage. 
    raw data is cleaned up and organized for the following stage of data processing.
    During preparation, raw data is diligently checked for any errors. 
    The purpose of this step is to eliminate bad data  (redundant, incomplete, or incorrect data) and begin to create high-quality data for the best
    """
    # post_availiable(products)
    avail = list()
    for prod in products:
        if prod['dataType'] == 'GRIB2':
            process_tiles(zoom=5, gribpath=prod['filePath'], validtime=prod['validTime'],
                          product=prod['layerName'], dirs=(TMP_IMG, TMP_DATA))

        elif prod['dataType'] == 'JSON':
            ps = process_probsevere(filepath=prod['filePath'])
            pass
        a = dict(layerName=prod['layerName'], validTime=prod['validTime'])
        avail.append(a)

    update_availiable_products(avail)
    return ps.feature_collection


def _collect(products):
    with open(products) as prods:
        base_products = np.array(pd.read_json(prods))
        # for product in base_products:
        bp = Fetch(base_products=base_products,
                   save_loc='tmp/', dtype='ndarray')

        return bp.features
    # with open(products) as prods:
    #     base_products = json.load(prods)
    #     bp = Fetch(base_products=base_products,
    #                dtype='ndarray', save_loc=TMP_RAW)
    #     return bp.features


def _manage(instance):
    if instance == 'START':
        for folder in directories:
            os.makedirs(folder, exist_ok=True)
    elif instance == 'STOP':
        rmtree('tmp/', ignore_errors=False, onerror=None)


def ldm_controller(req):
    """
    ## Steps

    #### collect:
        Opens baseProducts.json and pulls data from the MRMS Dataset using the Fetch module.

    #### prep:
        prep itterates through the dataset and calls the aplicable functions to process the data.  Additional 

    #### process:
        calls modules to process the grib and json data.

    #### write:
        stores the processed information into the mongodb database

    ##### manage:
        manage is called at the START and STOP.  manage

    """

    initial_timer = time.time()
    _manage('START')

    #####################|  COLLECT   |#####################
    intermediate_timer = time.time()
    base_products = _collect(req)
    print(f'data collection took \
            {round(time.time() - intermediate_timer)} seconds')

    #####################|  PREP   |#####################
    intermediate_timer = time.time()
    feature_collection = _prep(base_products)
    print(f'data processing took \
            {round(time.time() - intermediate_timer)} seconds')

    #####################|  WRITE   |#####################
    intermediate_timer = time.time()
    _write(feature_collection)
    print(f'data writing took \
            {round(time.time() - intermediate_timer)} seconds')

    _manage('STOP')

    print(f'total processing took \
            {round(time.time() - initial_timer)} seconds')


# ldm_controller('requests.json')
# data = [{
#     'dataType': 'GRIB2',
#     'layerName': 'CREF',
#     'urlPath': '2D/MergedReflectivityQCComposite/',
#     'validTime': '20210927-1530',
#     'filePath': 'tmp/MRMS_MergedReflectivityQCComposite_00.50_20210927-153027.grib2.gz'
# }, {
#     'dataType': 'GRIB2',
#     'layerName':
#     'VIL',
#     'urlPath':
#     '2D/LVL3_HighResVIL/',
#     'validTime': '20210927-1520', 'filePath': 'tmp/MRMS_LVL3_HighResVIL_00.50_20210927-152000.grib2.gz'},
#     {
#     'dataType': 'JSON', 'layerName': 'probSevere', 'urlPath': 'ProbSevere/PROBSEVERE/', 'validTime': '20210927-1532', 'filePath': 'tmp/MRMS_PROBSEVERE_20210927_153237.json'}]

# post_availiable(data)
# for d in data:
#     update_availiable(d)
