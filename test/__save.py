import re
import os
from glob import glob
from pymongo import MongoClient
from gridfs import GridFS
try:
    from dotenv import dotenv_values
    env = dotenv_values('.env')
    username = env['MONGO_USER']
    password = env['MONGO_PASSWORD']
    print('mongodb username and password loaded from dotenv')
except:
    print('failed to load dotenv')
    pass

##############|  MONGODB   |#################
url = f"mongodb+srv://{username}:{password}@wild-blue-yonder.jy40m.mongodb.net/database?retryWrites=true&w=majority"
client = MongoClient(url)
db = client.sigmet

# ?____________________________________________
# *
# *               COLLECTIONS
# ?____________________________________________
bp = db.baseProducts  # ? PRODUCT DIRECTORY METADATA
# ? FILESERVER COLLECTION
ps = db.probSevere  # ? PROBSEVERE COLLECTION


def save(x):
    paths = glob(os.path.join(f'tmp/data/{x.name}/*/*/*/', '*.png'))
    print(x.name, x.filename)
    [_write(open(path, 'rb')) for path in paths]

    # ? if baseproduct validTimes length is greater than 12 trim to 11
    is_long = len(x.validTimes) >= 12
    vt = x.validTimes[-11:] if is_long else x.validTimes
    vt.append(x.validtime)
    # ? update baseproduct directory with validTime list
    bp.update_one({"name": x.name}, {'$set': {'validTimes': vt}})
    if is_long:
        collection = f'{x.name}-{x.validTimes[0]}'
        print(f'dropping collection:\n {collection}')
        db.drop_collection(f'{collection}.files')
        db.drop_collection(f'{collection}.chunks')


def _parse(path):
    gex = r"(?<=tmp/data/)(.*)(?=/[0-9]/[0-9]/[0-9])(.*)"
    prod_vt, filename = re.search(gex, path).groups()
    collection = prod_vt.replace('/', '-')
    return collection, filename[1:]


def _write(img):
    col, fn = _parse(img.name)
    gfs = GridFS(db, collection=col)
    f = gfs.new_file(filename=fn)
    try:
        f.write(img)
    finally:
        f.close()


def init_dataset(name):
    collections = str(db.list_collection_names())
    dataset = rf'{name}-[0-9]*-[0-9]*'
    matching_names = re.findall(dataset, collections)

    for collection in matching_names:
        db.drop_collection(f'{collection}.files')
        db.drop_collection(f'{collection}.chunks')

    bp.update_one({"name": name}, {'$set': {'validTimes': []}})
