
from dps.controller import controller
# import os
# from glob import glob
from shutil import rmtree
# from dps.router import test
from dps.data_collection import collect, get_grouped_validtimes
from dps.data_processing import process
import json
import os
import numpy as np
# rmtree('tmp/', ignore_errors=False, onerror=None)
from dps.router import Router, bp, db
from glob import glob
from gridfs import GridFS
import re
import sched
import time

# route.gridfs(glob(os.path.join('tmp/data/*/*/*/*/', '*.png')))

paths = ['tmp/data', 'tmp/raw/', 'tmp/img/']
base_request = 'baseRequest.json'
features = json.load(open(base_request))['request']

nexrad_feature_names = []
for feature in features:
    if feature['prodType'] == 'NEXRAD':
        nexrad_feature_names.append(feature['name'])

    # print(feature)
print(nexrad_feature_names)


class TmpTree:
    def __init__(self, tmp, paths):
        self.tmp = tmp
        self.paths = paths

    def mk(self):
        for path in self.paths:
            os.makedirs(path, exist_ok=True)

    def rm(self):
        rmtree(self.tmp, ignore_errors=False, onerror=None)


route = Router()
tt = TmpTree('tmp/', paths)


def reinitialize_database(feature_names):
    for collection in db.list_collection_names():
        isTrue = bool(re.search(r'.*\.chunks$', collection)
                      ) or bool(re.search(r'.*\.files$', collection))

        if isTrue:
            print(f'removing {collection}')
            db.drop_collection(collection)
        else:
            pass
    # ? initalize MOSAIC
    for name in feature_names:
        bp.update_one({"name": name}, {'$set': {'validTimes': []}})


# reinitialize_database(nexrad_feature_names)


def dosome_more(sc):
    s.enter(300, 1, dosome_more, (sc,))
    # ? make tmp tree
    tt.mk()
    # ? collect raw data
    raw_data = collect(features)
    print(raw_data)
    for product, validtime, filepath in raw_data:
        # ? process data
        process(product, validtime, filepath)
        # ? write all files in the tmp tree to the database data
        route.gridfs(glob(os.path.join('tmp/data/*/*/*/*/', '*.png')))
        # ? list of avaiable valid times in product directory
        data = bp.find_one({"name": product}, {"validTimes": 1, '_id': 0})
        vt = data['validTimes']
        # ? slice the back of the array
        diff = len(vt)-24
        vts2db = vt[diff:]
        # ? append new value
        vts2db.append(validtime)
        # ? update product directoy
        print(f'\n{product} files & chunks created')
        print(f'updating product directory with\n validTime{validtime} ')
        bp.update_one({"name": product}, {'$set': {'validTimes': vts2db}})
        # ? with the removed time drop chunks and files
        vts2rm = vt[:diff]
        for vtRm in vts2rm:
            try:
                _files = f'{product}-{vtRm}.files'
                db.drop_collection(_files)
                _chunks = f'{product}-{vtRm}.chunks'
                db.drop_collection(_chunks)
                print(f'{_files} & {_chunks} succuffly removed')
            except:
                print('could not remove files and chunks')

            # files, chunks = route.get_gridfs(product, vtRm)
            # try:
            #     files.drop()
            #     chunks.drop()
            # except:
            #     print('could not drop files')
            # try:
            #     pass
            # except:
            #     failed

    tt.rm()


s = sched.scheduler(time.time, time.sleep)
s.enter(300, 1, dosome_more, (s,))
s.run()


# while True:
#     sleep(60 - time() % 300)
#     dosome_more(12)
# vt[diff:]

# print(vt_to_db)

# for
# print(vts_to_rm)
# print()
# print(np.diff([len(vt), 24]))
# if len(vt) > 24:
#     # print(vt[-:])
# files, chunks = route.get_gridfs(product, validtime)

# if len(db_data['validTimes']) > 24:
#     # db.lists.update({}, {$unset : {"interests.3" : 1 }})
#     # db.lists.update({}, {$pull : {"interests" : null}})
#     pass
# else:
#     pass
# print()
# for collection in bp.find({"name":product}):
#     col_vt=collection['validTimes']
#     col_vt.append(validtime)
#     if len(col_vt)>24:
#         # append and remove
#         # remove something from the list
#         pass
#     else:
#         print(col_vt)
# process(product,validtime,filepath)
# rmtree('tmp/', ignore_errors=False, onerror=None)
# print(raw_data)


# rmtree('tmp/', ignore_errors=False, onerror=None)
# test()
# controller(verbose=True)
# print(glob(os.path.join(f'tmp/data/*/*/*/*/', '*.png')))
# test(glob(os.path.join(f'tmp/data/*/*/*/*/', '*.png')))
