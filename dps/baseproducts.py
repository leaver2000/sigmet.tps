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


# from use.mongo import read_all, insert_many, post_collection
from dps.withMRMS import TileNames, Mosaic
# from modules.probsevere import ProbSevere
from dps.probsevere import ProbSevere
from dps.env import ld


DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)

regex = {
    'NEXRAD': r"(?!.*_)(.*)(?=.grib2.gz)",
    'PROBSEVERE': r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
}


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
    # raw = None
    # img = None
    # data = None
    # fileservice = glob(os.path.join(f'{data}*/*/*/*/', '*.png'))

    def __init__(self):
        # self.fil
        # self.raw, self.img, self.data = dirs

        with open('baseRequest.json')as br:
            self.features = json.load(br)['request']

        return None

    # *_____________| COLLECTION |______________

    def collect(self):
        for feat in self.features:
            fp, vt = self._retrieve_products(feat)
            feat['filePath'] = fp
            feat['validTimes'] = vt

    def _retrieve_products(self, feat):
        pageDir = self.url+feat['urlPath']
        page = pd.read_html(pageDir+self.query)
        prods = np.array(*page)[3:]
        prodType = feat['prodType']

        fn, vt = self._validate_products(prods=prods, prodType=prodType)

        filePath = ld.raw+fn  # f'{self.raw}{fn}'  # self.save_loc+fn

        request.urlretrieve(pageDir+fn, filePath)

        validtime = {
            "PROBSEVERE": vt.replace("_", "-"),
            "NEXRAD": vt
        }[prodType]

        return filePath, validtime

    def _validate_products(self, prods=None, prodType=None):
        for prod in prods:
            validTime = re.search(regex[prodType], prod[0]).group()[:-2]
            if int(validTime[12:]) == 0:
                vt = validTime \
                    if prodType == 'NEXRAD' \
                    else validTime.replace('_', '-')
                return (prod[0], vt)
            else:
                continue

    # *_____________| PROCESSING |______________

    def process(self):
        for feat in self.features:
            featType = feat['prodType']
            vt = feat['validTimes']
            fp = feat['filePath']

            if featType == "PROBSEVERE":
                with open(fp, 'r') as f:
                    fc = json.load(f)
                    # The probsevere features are passed to the probsevere module
                    ps = ProbSevere(valid_time=vt, features=fc['features'])
                    # The probsevere feature colleciton is attached to the baseproduct class.
                    # The ldm can then access the probsevere feature collection via
                    self.probsevere = ps.feature_collection

            elif featType == "NEXRAD":
                self._process_tiles(validtime=vt, product=feat['name'],
                                    zoom=5, gribpath=fp)

    def _process_tiles(self, gribpath=None, zoom=None,
                       validtime=None, product=None):

        dpi = np.multiply(150, zoom)
        img_source = f'{product}-{validtime}-{zoom}'

        # set zxy params via the TileNames Class
        tn = TileNames(latrange=DESIRED_LATRANGE,
                       lonrange=DESIRED_LONRANGE,
                       zooms=zoom, verbose=False)

        # wrapper for the MMM-py MosaicDisplay class
        display = Mosaic(gribfile=gribpath, dpi=dpi, work_dir=ld.img,
                         latrange=tn.latrange, lonrange=tn.lonrange)

        # wrapper for the MMM-py plot_horiz function
        file = display.render_source(filename=img_source)

        # using the provided tile names slice the Mosaic image into a slippy map directory

        display.crop_tiles(file=file, tmp=ld.data, product=product,
                           validtime=validtime, zoom=zoom, tile_names=tn)
        plt.close('all')
