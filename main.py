
from dps.controller import controller
# import os
# from glob import glob
from shutil import rmtree
# from dps.router import test
from dps.data_collection import collect
from dps.data_processing import process
import json
import os
# rmtree('tmp/', ignore_errors=False, onerror=None)
from dps.router import bp
tmp_paths = ['tmp/data','tmp/raw/','tmp/img/']
for path in tmp_paths:
    os.makedirs(path, exist_ok=True)


with open('baseRequest.json')as br:
    features = json.load(br)['request']

raw_data  = collect(features)

# print(raw_data)
# print(raw_data)
# for x in bp.find({},{"name": ,}):
#     print(x)




for product,validtime,filepath in raw_data:
    print(product)
    bp.update_one({"name":product}, {'$push': {'validTimes': validtime}})
    db_data = bp.find_one({"name":product})
    if len(db_data['validTimes']) > 24:
# db.lists.update({}, {$unset : {"interests.3" : 1 }}) 
# db.lists.update({}, {$pull : {"interests" : null}})
        pass
    else:

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





rmtree('tmp/', ignore_errors=False, onerror=None)
# print(raw_data)



# rmtree('tmp/', ignore_errors=False, onerror=None)
# test()
# controller(verbose=True)
# print(glob(os.path.join(f'tmp/data/*/*/*/*/', '*.png')))
# test(glob(os.path.join(f'tmp/data/*/*/*/*/', '*.png')))
