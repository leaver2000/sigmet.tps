import os
import re
from time import time
from glob import glob
import json
from shutil import rmtree
from pprint import pprint
from urllib import request

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from modules.util import Gex
from modules.withMongo import read_all, post_all, post_collection, update_directory
from modules.withMRMS import TileNames, Mosaic
# from modules.probsevere import ProbSevere

DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)
TMP_RAW = 'tmp/raw/'
TMP_IMG = 'tmp/img/'
TMP_DATA = 'tmp/data/'
directories = (TMP_RAW, TMP_IMG, TMP_DATA)

##############|  REGEX   |#################
RE_DATA = r"(?<=tmp/data/)(.*)"
GLB_DATA = TMP_DATA+'*/*/*/*/'


class BaseProducts:
    """
    ## BaseProducts

    This class serves as an API to many other modules within the LDM library.

    The __init__ fn calls to mongodb base product collection to retreive a list of avaliable products.
    If the list is empty the class will open try to open a base_products.json file,
    and update mongoDB with the baseproduct collection.  This is usefull when mongodb needs to be updated.
    Update the base_products.json file and dump collection, and the class will reinitialize the collection. 


    - Provides a list of avaiable products and the ncep url and path to retreive them.

    - As data is removed and updated from the from the various collections within mongo db
    this class is meant to manage their state.  

    - Removing expired products from the db.

    - Maintain the validtime list in the dataabse, this allows the client application 
    to make a single request to the database and know what product valid times are avaiable.



    ### EXPLICT ROLES:

        - provide API for data retreival
        - update & remove old products
        - manage valid time state

    ### Usage

    bp=BaseProducts()

    bp.url ->"https://mrms.ncep.noaa.gov/data/"

    bp.query -> "?C=M;O=D"

    bp.request -> {'name': 'CREF', 'longName': 'MRMS Merged Composite Reflectivity', 'dtype': 'GRIB2', 'path': '2D/MergedReflectivityQCComposite/'.....

    """

    url = "https://mrms.ncep.noaa.gov/data/"
    query = "?C=M;O=D"
    # features = list()

    def __init__(self, probsevere=None):
        self.probsevere = probsevere
        collection = 'BASEPRODUCTS'

        try:
            base_req = read_all(collection=collection)

            if len(base_req) == 0:
                with open('base_products.json')as base_products:
                    base_req = json.load(base_products)['request']
                    post_all(base_req, collection=collection)
                    self.features = base_req

            else:
                self.features = base_req

            return

        except:
            print('sum tin wong')

        return None

    ######################## |  COLLECTION STAGE| ####################################

    def collect(self, save_loc=None):
        self.save_loc = save_loc
        for feat in self.features:
            fp, vt = self._get_prods(feat)
            feat['filePath'] = fp
            feat['validTimes'].append(vt)

        # pprint(self.features)

    def _get_prods(self, feat):
        page_dir = self.url+feat['urlPath']
        page = pd.read_html(page_dir+self.query)
        fn, vt = self._validate_time(
            layer_prods=np.array(*page)[3:], dtype=feat['dtype'])

        file_path = self.save_loc+fn

        request.urlretrieve(page_dir+fn, file_path)

        if feat['dtype'] == 'JSON':
            validtime = vt.replace("_", "-")
            self.raw_json = feat
        else:
            validtime = vt

        # validtime = vt.replace("_", "-") if feat['dtype'] == 'JSON' else vt

        return file_path, validtime

    def _validate_time(self, layer_prods=None, dtype=None):

        regex = Gex.grib_vt if dtype == 'GRIB2' else Gex.json_vt
        for prods in layer_prods:
            valid_time = re.search(regex, prods[0]).group()[:-2]

            if int(valid_time[12:]) == 0:
                return (prods[0], valid_time)
            else:
                continue
    ######################## |  PREPARE AND PROCESS STAGE    | ####################################

    def prepare_and_process(self, dtype=None):
        # print(self.raw_json)
        if dtype == "JSON":
            self._process_probsevere(filepath=self.raw_json['filePath'])
            return

        elif dtype == "GRIB2":
            features = [
                feat for feat in self.features if feat["dtype"] == dtype]
            for feat in features:
                self._process_tiles(zoom=5, gribpath=feat['filePath'], validtime=feat['validTimes'][-1],
                                    product=feat['name'], dirs=(TMP_IMG, TMP_DATA))

    def _process_tiles(self, gribpath=None, zoom=None,
                       validtime=None, product=None, dirs=None):

        img, data = dirs
        dpi = np.multiply(150, zoom)
        img_source = f'{product}-{validtime}-{zoom}'

        # set zxy params via the TileNames Class
        tn = TileNames(latrange=DESIRED_LATRANGE,
                       lonrange=DESIRED_LONRANGE,
                       zooms=zoom, verbose=False)

        # wrapper for the MMM-py MosaicDisplay class
        display = Mosaic(gribfile=gribpath, dpi=dpi, work_dir=img,
                         latrange=tn.latrange, lonrange=tn.lonrange)

        # wrapper for the MMM-py plot_horiz function
        file = display.render_source(filename=img_source)

        # using the provided tile names slice the Mosaic image into a slippy map directory
        display.crop_tiles(file=file, tmp=data, product=product,
                           validtime=validtime, zoom=zoom, tile_names=tn)
        plt.close('all')

    def _process_probsevere(self, filepath=None):

        with open(filepath, 'r') as f:
            fc = json.load(f)
            vt = fc['validTime'][:-6].replace('_', '-')
            feats = fc['features']
            self.probsevere.set_features(valid_time=vt, features=feats)

    ######################## |  PREPARE AND PROCESS STAGE    | ####################################

    def commit_and_post(self):
        # only the probSevere JSON data is
        # passed to this function.
        # post_collection(data, collection='PROBSEVERE')
        post_collection(self.probsevere.feature_collection,
                        collection='PROBSEVERE')

        for filename in glob(os.path.join(GLB_DATA, '*.png')):
            with open(filename, 'rb') as tile:
                post_collection(tile, collection='FILESERVER')

        update_directory(self)
        return

    def maintain_tmp_tree(self, instance):
        if instance == 'START':
            for folder in directories:
                os.makedirs(folder, exist_ok=True)
            return time()

        elif instance == 'STOP':
            rmtree('tmp/', ignore_errors=False, onerror=None)
            return time()
        # pass
    # avail = list()
    # # print()
    # for prod in bp.features:
    #     validtime = prod['validTimes'][-1]
        # if prod['dtype'] == 'GRIB2':
        #     process_tiles(zoom=5, gribpath=prod['filePath'], validtime=validtime,
        #                   product=prod['name'], dirs=(TMP_IMG, TMP_DATA))

        # elif prod['dtype'] == 'JSON':
        #     ps = process_probsevere(filepath=prod['filePath'])
        #     pass
        # a = dict(layerName=prod['name'], validTime=validtime)
        # avail.append(a)

    # return ps.feature_collection
# base = BaseProducts()
# print(base)
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
# from modules.withMRMS import TileNames, Mosaic, ProbSevere

# DESIRED_LATRANGE = (20, 55)
# DESIRED_LONRANGE = (-130, -60)


# def process_tiles(gribpath=None, gribfile=None, zoom=None,
#                   validtime=None, product=None, dirs=None):

#     img, data = dirs
#     dpi = np.multiply(150, zoom)
#     img_source = f'{product}-{validtime}-{zoom}'

#     # set zxy params via the TileNames Class
#     tn = TileNames(latrange=DESIRED_LATRANGE,
#                    lonrange=DESIRED_LONRANGE,
#                    zooms=zoom, verbose=False)

#     # wrapper for the MMM-py MosaicDisplay class
#     display = Mosaic(gribfile=gribpath, dpi=dpi, work_dir=img,
#                      latrange=tn.latrange, lonrange=tn.lonrange)

#     # wrapper for the MMM-py plot_horiz function
#     file = display.render_source(filename=img_source)

#     # using the provided tile names slice the Mosaic image into a slippy map directory
#     display.crop_tiles(file=file, tmp=data, product=product,
#                        validtime=validtime, zoom=zoom, tile_names=tn)
#     plt.close('all')


# def process_probsevere(filepath=None):
#     if filepath is None:
#         print('a file path was not provided')
#     else:
#         with open(filepath, 'rb') as f:
#             fc = np.array(pd.read_json(f))
#             return ProbSevere(feature_collection=fc)
