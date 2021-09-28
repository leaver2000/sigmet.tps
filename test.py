import os
from pprint import pprint
import json
from glob import glob
from urllib import request
#############
import pandas as pd
import numpy as np
from modules.probsevere import ProbSevere
URL = "https://mrms.ncep.noaa.gov/data/ProbSevere/PROBSEVERE/"
QUERY = "?C=M;O=D"

ps = ProbSevere()


def download_sample_json():
    page = np.array(pd.read_html(URL+QUERY))
    # ? pandas returns a 3dim array
    # ? np.squeeze reduces the dims 1lvl
    page_directory = np.squeeze(page)[2:15]
    # ? the first 2 arrays in in the page
    # ? are irrelivant
    for path in page_directory:
        request.urlretrieve(URL+path[0], 'data/'+path[0])


def read_sample_json():
    for file in glob(os.path.join('data/', '*.json')):
        with open(file, 'r') as f:
            fc = json.load(f)
            vt = fc['validTime'][:-6].replace('_', '-')
            feats = fc['features']
            ps.set_features(valid_time=vt, features=feats)

    print(ps.list_np_plots())
    # print(vt)
    # pprint(feats)
    # print(ps.feature_collection)


read_sample_json()
#     with open(filepath, 'r') as f:
#         fc = json.load(f)
#         vt = fc['validTime'][:-6].replace('_', '-')
#         feats = fc['features']
#         self.probsevere.set(valid_time=vt, features=feats)

# print(filename)
# with open(filename, 'rb') as tile:
#     post_collection(tile, collection='FILESERVER')

# print(path[0])


# v = np.where(a == '361K')
# print(a[0:3:3])
# page.flatten()
# print()
# _, l, d = page.shape
# # a = page.reshape((d))
# a = page.reshape(l, d)
# print(a)
# np.array(page)


# ps = ProbSevere()

# def _get_prods(self, feat):
#     page_dir = self.url+feat['urlPath']
#     page = pd.read_html(page_dir+self.query)
#     fn, vt = self._validate_time(
#         layer_prods=np.array(*page)[3:], dtype=feat['dtype'])

#     file_path = self.save_loc+fn

#     request.urlretrieve(page_dir+fn, file_path)

#     if feat['dtype'] == 'JSON':
#         validtime = vt.replace("_", "-")
#         self.raw_json = feat
#     else:
#         validtime = vt