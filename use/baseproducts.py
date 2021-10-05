import os
import re
# from time import time
from glob import glob
import json
# from shutil import rmtree
# from pprint import pprint
from urllib import request

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from use.util import Gex
# from use.mongo import read_all, insert_many, post_collection
from use.withMRMS import TileNames, Mosaic
# from modules.probsevere import ProbSevere
from use.probsevere import ProbSevere
DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)
DIRS = ('tmp/img/', 'tmp/data/')
regex = {
    'NEXRAD': r"(?!.*_)(.*)(?=.grib2.gz)",
    'PROBSEVERE': r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
}


# class Product:
#     validtime = None


# p = Product()


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
    valid_time = {}
    fileservice = glob(os.path.join('tmp/data/*/*/*/*/', '*.png'))

    def __init__(self):
        with open('baseRequest.json')as br:
            self.features = json.load(br)['request']

        return None

    ######################## |  COLLECTION STAGE| ####################################

    def collect(self, save_loc=None):
        self.save_loc = save_loc
        for feat in self.features:
            fp, vt = self._get_prods(feat)
            feat['filePath'] = fp
            feat['validTime'] = vt

    def _get_prods(self, feat):
        page_dir = self.url+feat['urlPath']
        page = pd.read_html(page_dir+self.query)
        prodType = feat['prodType']
        fn, vt = self._validate_time(
            layer_prods=np.array(*page)[3:], prodType=prodType)

        file_path = self.save_loc+fn

        request.urlretrieve(page_dir+fn, file_path)

        if feat['prodType'] == 'PROBSEVERE':
            self.raw_json = feat
        validtime = {
            "PROBSEVERE": vt.replace("_", "-"),
            "NEXRAD": vt
        }[prodType]
        # validtime = vt.replace("_", "-") if feat['dtype'] == 'JSON' else vt

        return file_path, validtime

    def _validate_time(self, layer_prods=None, prodType=None):
        for prods in layer_prods:
            valid_time = re.search(regex[prodType], prods[0]).group()[:-2]
            if int(valid_time[12:]) == 0:
                vt = valid_time \
                    if prodType == 'NEXRAD' \
                    else valid_time.replace('_', '-')
                return (prods[0], vt)
            else:
                continue
    ######################## |  PREPARE AND PROCESS STAGE    | ####################################

    def prepare(self):
        for feat in self.features:
            featType = feat['prodType']
            vt = feat['validTime']
            fp = feat['filePath']

            if featType == "PROBSEVERE":
                with open(fp, 'r') as f:
                    fc = json.load(f)
                    # The probsevere features are passed to the probsevere module
                    ps = ProbSevere(valid_time=vt, features=fc['features'])
                    # The probsevere feature colleciton is attached to the baseproduct class.
                    # The ldm can then access the probsevere feature collection via
                    # bp = BaseProducts()
                    # bp.prep()
                    # bp.probsevere
                    self.probsevere = ps.feature_collection

            elif featType == "NEXRAD":
                self._process_tiles(zoom=5, gribpath=fp,
                                    validtime=vt,
                                    product=feat['name'], dirs=DIRS)

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

    # def commit_and_post(self):
    #     # only the probSevere JSON data is
    #     # passed to this function.
    #     # post_collection(data, collection='PROBSEVERE')
    #     post_collection(self.probsevere.feature_collection,
    #                     collection='PROBSEVERE')

    #     for filename in glob(os.path.join(GLB_DATA, '*.png')):
    #         with open(filename, 'rb') as tile:
    #             post_collection(tile, collection='FILESERVER')

    #     # update_directory(self)
    #     return
