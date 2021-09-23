
import re
import os
import sys
import threading
import time
import json
from shutil import rmtree
from urllib import request
import pandas as pd
import numpy as np
DEST_PATH = 'data/'
WORK_PATH = 'tmp/'
RAWDATA = f'{WORK_PATH}raw/'
##############|  DEFAULT UTIL  |#################
BGCOLOR = '#000000'
RE_GRIB_VALIDTIME = r"(?!.*_)(.*)(?=.grib2.gz)"
RE_JSON_VALIDTIME = r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
##############|  DEFAULT REQUEST  |#################
BASE_URL = 'https://mrms.ncep.noaa.gov/data/'
BASE_PRODUCTS = [{
    'dataType': 'GRIB2',
    'layerName': 'CREF',
    'urlPath': '2D/MergedReflectivityQCComposite/',
    'latest': True

}, {
    'dataType': 'GRIB2',
    'layerName': 'VIL',
    'urlPath': '2D/LVL3_HighResVIL/',
    'latest': True

}, {
    'dataType': 'GeoJSON',
    'layerName': 'probSevere',
    'urlPath': 'ProbSevere/PROBSEVERE/',
    'query': '?C=M;O=D',
    'latest': True
}]


class Fetch:
    """
    # FetchData

    Get current data serves as the local data manager for the GenerateMosaic Class.  GCD's role is to access data from
    the NSSL dataset.  Passing an list of objects with the path to the layer directory and a layername. GCD will retreive
    and store the raw data locally for later processing. GCD Returns an object with information specific to the raw data
    that was retreived, such as the validTime and localPath directory to the raw data.

    This list can then be passed to the GenerateMosaic():

    class where the information will be degribed and processed into a WMTS friendly format.

    example usage....

    data = GetCurrentData(LAYERS)

    GenerateMosaic(data.layers)

    -----------------------------------------------------------------------------
    """

    def __init__(self, layers=BASE_PRODUCTS):

        os.makedirs(RAWDATA, exist_ok=True)
        self.baseurl = BASE_URL
        self.layers = layers
        self.grib_data = list()
        self.json_data = list()

        try:
            for layer in self.layers:
                try:
                    if layer['dataType'] == 'GRIB2':
                        self._get_grib2(layer)
                    if layer['dataType'] == 'GeoJSON':
                        self._get_geojson(layer)

                    # self._retreive_data(layer)
                except:
                    print('there was an error in the data request for the layer',
                          layer['layerName'])

        except:
            print('there was an error in the initial layer request')

    def _regex():

        return

    def _get_geojson(self, layer):
        layer_directory = self.baseurl+layer['urlPath']
        # page = pd.read_html(layer_directory+layer['query'])?C=M;O=D
        page = pd.read_html(f'{layer_directory}?C=M;O=D')
        layer_product = np.array(page)[0][2][0]

        # print(layer_directory+layer_product)
        request.urlretrieve(layer_directory+layer_product,
                            RAWDATA+layer_product)
        # regex = r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
        # RE_JSON_VALIDTIME=r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
        validtime = re.search(RE_JSON_VALIDTIME, layer_product).group()[:-2]

        layer['validTime'] = validtime.replace("_", "-")
        layer['filePath'] = RAWDATA+layer_product

    def _validate_time(self, layer_prods=None):

        # regex = r"(?!.*_)(.*)(?=.grib2.gz)"
        for prods in layer_prods:
            valid_time = re.search(RE_GRIB_VALIDTIME, prods[0]).group()[:-2]

            if int(valid_time[12:]) == 0:

                return (prods[0], valid_time)
            else:
                print('skipping non-zero interval')
                continue

    def _get_grib2(self, layer):
        layer_directory = self.baseurl+layer['urlPath']  # +layer['query']
        page = pd.read_html(f'{layer_directory}?C=M;O=D')  # ?C=M;O=D

        layer_product, validtime = self._validate_time(
            layer_prods=np.array(*page)[3:])

        request.urlretrieve(layer_directory+layer_product,
                            RAWDATA+layer_product)

        layer['validTime'] = validtime
        layer['filePath'] = RAWDATA+layer_product
        self.grib_data.append(RAWDATA+layer_product)


# print('hello nodemon')
# product = Fetch(layers=BASE_PRODUCTS)

# for prod in product.layers:
#     print('')
#     print('|-- DATA RETREIVED --|')
#     print(f"    layerName = {prod['layerName']}")
#     print(f"    validTime = {prod['validTime']}")
#     print(f"    filePath = {prod['filePath']}\n")

class UseRequest:
    def __init__(self, basepath):
        self.basepath = basepath
        return

    def get(self, path, params):
        url = f'{self.basepath}'


def diag(j):
    print(json.dumps(j, indent=4, sort_keys=True))


with open('baseProducts.json') as f:
    data = json.load(f)
    baseurl = data['baseUrl']
    # print(baseurl)
    mrms = UseRequest(baseurl)

    for req in data['request']:
        print(req['urlPath'],)
        # mrms.get()
        pass
        # diag(req)
