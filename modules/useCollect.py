import re
import numpy as np
import pandas as pd
from urllib import request
from modules.util import Gex


class Fetch:
    features = list()

    def __init__(self, base_products=None, dtype=None, save_loc=None):
        self.save_loc = save_loc

        if dtype is None:
            print('a dtype was not specified')

        elif dtype == 'ndarray':
            for i, product in enumerate(base_products):
                if i == 0:
                    self.baseurl, self.query, features = product
                    self._get_prods(features)
                else:
                    self._get_prods(product[2])

        elif dtype == 'JSON':
            self.baseurl = base_products['baseUrl']
            self.query = base_products['query']

            for feature in base_products['layers']:
                self._get_prods(feature)

        print(self.features)

    def _get_prods(self, layer):
        self.features.append(layer)
        layer_directory = self.baseurl+layer['urlPath']
        page = pd.read_html(layer_directory+self.query)

        layer_product, validtime = self._validate_time(
            layer_prods=np.array(*page)[3:], dtype=layer['dataType'])

        request.urlretrieve(layer_directory+layer_product,
                            self.save_loc+layer_product)

        layer['validTime'] = validtime if layer['dataType'] == 'GRIB2' else validtime.replace(
            "_", "-")
        layer['filePath'] = self.save_loc+layer_product

    def _validate_time(self, layer_prods=None, dtype=None):

        regex = Gex.grib_vt if dtype == 'GRIB2' else Gex.json_vt
        for prods in layer_prods:
            valid_time = re.search(regex, prods[0]).group()[:-2]

            if int(valid_time[12:]) == 0:
                return (prods[0], valid_time)

            else:
                # print('skipping non-zero interval')
                continue
