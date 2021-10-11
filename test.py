import json
from dps.models import get_gridfs, bp
# from dps.data_collection import collect
from dps.data_processing import process
from types import SimpleNamespace
import numpy as np
from datetime import datetime, timedelta
from shutil import rmtree
import os
import pandas as pd
import re
base_request = 'baseRequest.json'
features = json.load(open(base_request))

def dumpJSON(req):
    jd=json.dumps(req)
    return json.loads(jd, object_hook=lambda d: SimpleNamespace(**d))

def scrape_dataset(x):
    url = f"https://mrms.ncep.noaa.gov/data/{x.urlPath}"
    query = "?C=M;O=D"
    gex = r"(?!.*_)(.*)(?=.grib2.gz)"
    page = pd.read_html(url+query)
    prods = np.array(*page)[3:-1]
    flat_arr=prods[:,[0]].flatten()
    # print(flatt_arr)


    # x = np.where(np.datetime64(flat_arr) ==0)
    # print(x)
    for a in flat_arr:
        s = re.search(gex,a).group()
        new_vt = datetime.strptime(s, '%Y%m%d-%H%M%S')

        if (new_vt.minute % 10 ==0):
            print(x.name, new_vt)
            break
        # print(a)

    # for a in flat_arr:
    #     s = re.search(gex,a).group()
    #     new_vt = datetime.strptime(s, '%Y%m%d-%H%M%S')
        # print(type(new_vt.minute),new_vt.minute==10)
        # if new_vt.minute == timedelta(minutes=10):
        #     print(new_vt)
        #     break
        # else:
        #     continue
        # delta = timedelta(minutes=10)
        # # if 0 < new_vt.total_seconds() < delta.total_seconds():
        # # print(x.name,new_vt,delta)
        # print(new_vt.minute)
        # # print(dir(new_vt))





def parse_time(vt):
    return datetime.strptime(vt, '%Y%m%d-%H%M')



for feat in features['request']:
    x = dumpJSON(feat)
    validTimes = bp.find_one({"name": x.name}, {"validTimes": 1, '_id': 0})['validTimes']
    nowT = datetime.now()
    minT = parse_time(validTimes[-1])
    timeDelta = np.abs((minT - nowT))
    expried_db=timeDelta.total_seconds() > 600
    scrape_dataset(x)

    if expried_db:
        print('scrapping dataset')
        # scrape_dataset(x)
        pass

    else:
        print(timeDelta)




def collect(collections):
    # for key_names, min_time in collections:
    print(collections)
    # for 





def run():
    paths = ['tmp/data', 'tmp/raw/', 'tmp/img/']
    [os.makedirs(path, exist_ok=True)for path in paths]
   
    grib_data = collect(features)
    # for product, validtime, filepath in grib_data:
    #     process(product, validtime, filepath)






    # rmtree('tmp/', ignore_errors=False, onerror=None)
# run()
# b = collect(features)
# print(b)




# files,chunks = get_gridfs('CREF','20201012')#[f'data{vm}'for vm in ['.files','.chunks']]



# print(dir(files),chunks)