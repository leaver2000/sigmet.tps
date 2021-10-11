# from use.util import Gex, Env
import numpy as np
from pymongo import MongoClient
from gridfs import GridFS
import re
from dps.env import url
import json
# import base64
# import bson
from time import time
from datetime import datetime, time
import pandas as pd
from urllib import request
# ?____________________________________________
# *
# *                 DATABASE
# ?____________________________________________
client = MongoClient(url)
db = client.sigmet

# ?____________________________________________
# *
# *               COLLECTIONS
# ?____________________________________________
bp = db.baseProducts  # ? PRODUCT DIRECTORY METADATA
# ? FILESERVER COLLECTION
ps = db.probSevere  # ? PROBSEVERE COLLECTION

"""
base_requests:
Contains the information used to scrape and 
collect information from MRMS dataset.The 
base Request can be update by updating the
base_products.json file and dumping the
collection, the base products class will then
update the database with new request information.

base_products:
Contains the database metadata ie: 
what products and valid times are available
to the client side webapplication
"""
# [A-Z]+?(?=-)
# (?<=[A-Z]-)(.*)
# ([A-Z]+?(?=-) )  [(?<=[A-Z]-)(.*)]

# def parse_collection_name(container,collection):
#     col = re.search(r".+?(?=.files)", collection)
#     if col is not None:
#         name,validtime =col.group().split('-',1)
#         print(validtime)
#         try:
#             container[name]+=[validtime]
#         except:
#             container[name]=[validtime]


# url = "https://mrms.ncep.noaa.gov/data/"
# query = "?C=M;O=D"
# regex = {
#     'NEXRAD': r"(?!.*_)(.*)(?=.grib2.gz)",
#     'PROBSEVERE': r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
# }

class DatabaseRoutes:
    def gridfs(self, paths):
        print(paths)
        pass


class Router:
    def get_gridfs(self, prod, vt):
        col = f'{prod}-{vt}'

        files = GridFS(db, collection=f'{col}.files')
        chunks = GridFS(db, collection=f'{col}.chunks')

        # print()
        return (files, chunks)

    def gridfs(self, paths):
        # arr = []
        for path in paths:
            with open(path, 'rb') as img:
                col, fn = self._parse(img.name)
                gfs = GridFS(db, collection=col)
                f = gfs.new_file(filename=fn)
                print(f)
                try:
                    f.write(img)
                finally:
                    f.close()
        #             arr.append([col, fn])
        # return arr

    def _parse(self, filepath):
        gex = r"(?<=tmp/data/)(.*)(?=/[0-9]/[0-9]/[0-9])(.*)"
        prod_vt, filename = re.search(gex, filepath).groups()
        collection = prod_vt.replace('/', '-')
        # filename = zxypng[1:]
        return collection, filename[1:]

    def probsevere(self, data):
        ps.insert_one(data)

    def done(self, features):
        # * itterating over all of the newly created base_product features
        for d in features:
            print(d)
            name = d['name']
            vt = d['validTimes']

            # * removing dps specific stored feature information
            del d['urlPath']
            del d['filePath']

            # * collecting the exsisting database information
            res = bp.find_one({'name': name})

            # * if feature does not exist a new named feature is created
            if res is None:
                print(f'initializing database with new base product.. {name}')
                d['validTimes'] = [vt]
                bp.insert_one(d)

            # * otherwise the database named feature validtimes are updated
            else:
                # ? call to self._manage_valid_times()
                validTimes = self._manage_valid_times(res['validTimes'], vt)

                print(
                    f'updating exsiting {name} collection with new validtime.. {vt}')
                _id = {'_id': res['_id']}

                bp.update_one(_id, {"$set": {"validTimes": validTimes}})

    # * _manage_valid_times trims the available baseproduct validtime listing
    #! additinoal functions need to be developed to remove  entire collections
    #! from the database after they are not longer made avaliable to the client

    def _manage_valid_times(self, collection, update):
        a = np.array([*collection, update])
        arr = a.flatten()
        if len(arr) > 12:
            print('trimming validtime')
            return np.delete(arr, 0).tolist()  # arr[1:11].tolist()
        else:
            return arr.tolist()
