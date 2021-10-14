import json
from time import time
from datetime import datetime, time
import pandas as pd
from urllib import request
from dps.router import db
import numpy as np
import re
url = "https://mrms.ncep.noaa.gov/data/"
query = "?C=M;O=D"
regex = {
    'NEXRAD': r"(?!.*_)(.*)(?=.grib2.gz)",
    'PROBSEVERE': r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
}


def collect(features):
    raw_data = []
    collections = _collections_to_get()
    try:
        for key_names, min_time in collections:
            prod = [item for item in features if item.get(
                'name') == key_names][0]
            new_vt, filepath = retrieve_products(prod, min_vt=min_time)
            raw_data.append([key_names, new_vt, filepath])
    except:
        print(f'failed to get {collections}')
        print(features)
        for feat in features:
            if feat["prodType"] == 'NEXRAD':
                new_vt, filepath = retrieve_products(feat, min_vt=None)
                raw_data.append([feat['name'], new_vt, filepath])
                # print(new_vt, filepath)

            # 'prodType': 'NEXRAD'

        # new_vt, filepath = retrieve_products(prod, min_vt=None)
        # raw_data.append([key_names, new_vt, filepath])

    # print(raw_data)
    return raw_data

# ? collections to get reads the database collections
# ? and determines if the most recent file is more than
# ? 5 mins old


def _collections_to_get():
    prods = []
    # min_times =[]
    collections = get_grouped_validtimes()
    max_seconds = 300
    # the max most recent file is comparied to the current time
    # if the current time is more than 300 seconds 5 mins old a new file is retreived

    if collections is None:
        pass
    else:
        for key in collections.keys():
            nowT = datetime.now()
            minT = np.max(collections[key])
            print(minT)
            timeDelta = np.abs((minT - nowT))
            if timeDelta.total_seconds() > max_seconds:
                prods.append([key, minT])
                # min_times.append(minT)
        return prods  # [prod_keys,min_times]#[[prod_keys],[min_times]]

# group all of the availiable valid times
# from the mongo db directory


def get_grouped_validtimes():

    container = {}
    for collection in db.list_collection_names():
        col = re.search(r".+?(?=.files)", collection)

        if col is not None:
            name, validtime = col.group().split('-', 1)
            dtime = datetime.strptime(validtime, '%Y%m%d-%H%M')

            try:
                container[name] += [dtime]

            except:
                container[name] = [dtime]
        else:
            return None

    return container


def retrieve_products(feat, min_vt=None):
    # print(min_vt)
    # products_to_render = []

    pageDir = url+feat['urlPath']
    page = pd.read_html(pageDir+query)
    prods = np.array(*page)[3:]
    prodType = feat['prodType']

    fn, str_vt = validate_products(prods=prods, prodType=prodType)
    new_vt = datetime.strptime(str_vt, '%Y%m%d-%H%M')

    # if the new validtime is greater than the oldest product
    # in the database get a new product
    print(min_vt, new_vt)
    if min_vt is None or min_vt < new_vt:
        filePath = 'tmp/raw/'+fn  # f'{self.raw}{fn}'  # self.save_loc+fn
        request.urlretrieve(pageDir+fn, filePath)
        print(str_vt, filePath)

        return str_vt, filePath
    # return products_to_render


# parse the html page directory and
# get time intervals of 0 or 6
# if the time interval is 6 change it to 5
def validate_products(prods=None, prodType=None):
    for prod in prods:
        validTime = re.search(regex[prodType], prod[0]).group()[:-2]
        inVt = int(validTime[12:])
        vt = validTime.replace('_', '-')

        if inVt == 0:
            return (prod[0], vt)
        elif inVt == 6:
            return (prod[0], f'{vt[:-1]}5')
        else:
            continue
