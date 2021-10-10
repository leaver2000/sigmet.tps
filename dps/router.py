# from use.util import Gex, Env
import numpy as np
from pymongo import MongoClient
from gridfs import GridFS
import re
from dps.env import url
# import base64
# import bson
from time import time

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


def test():
    print(db.list_collection_names())
    for collection in db.list_collection_names():
        # gex = r".+?(?=.files|.chunks)"
        col = re.search(r".+?(?=.files)", collection)
        if col is not None:
            a = col.group()
            print(a, str(time())[:4])


class Router:

    def gridfs(self, paths):
        for path in paths:
            with open(path, 'rb') as img:
                col, fn = self._parse(img.name)
                gfs = GridFS(db, collection=col)
                f = gfs.new_file(filename=fn)
                try:
                    f.write(img)
                finally:
                    f.close()

    def _parse(self, filepath):
        gex = r"(?<=tmp/data/)(.*)(?=/[0-9]/[0-9]/[0-9])(.*)"
        prod_vt, zxypng = re.search(gex, filepath).groups()
        collection = prod_vt.replace('/', '-')
        filename = zxypng[1:]
        return collection, filename

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
