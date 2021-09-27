import json
import pandas as pd
import numpy as np
import time
from shutil import rmtree
import os
from modules.useCollect import Fetch
import json
REQUESTS = 'requests.json'


def fetch_test(req):

    start = time.time()
    rmtree('tmp/', ignore_errors=False, onerror=None)
    os.makedirs('tmp/', exist_ok=True)
    with open(req) as prods:
        base_products = np.array(pd.read_json(prods))
        Fetch(base_products=base_products, save_loc='tmp/', dtype='ndarray')
    end = time.time()
    print(end-start)

    start = time.time()
    rmtree('tmp/', ignore_errors=False, onerror=None)
    os.makedirs('tmp/', exist_ok=True)
    with open(req) as prods:
        base_products = json.load(prods)
        Fetch(base_products=base_products, save_loc='tmp/', dtype='JSON')
    end = time.time()
    print(end-start)


# fetch_test(REQUESTS)
