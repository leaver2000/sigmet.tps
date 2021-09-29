import os
from pprint import pprint
import json
from glob import glob
from urllib import request
#############
import pandas as pd
import numpy as np
from use.probsevere import ProbSevere
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


read_sample_json()
