import re
import os
from glob import glob
from pymongo import MongoClient
from gridfs import GridFS

from dps.zxyMosaic import TileNames, Mosaic
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import re
from urllib import request
from datetime import datetime
try:
    from dotenv import dotenv_values
    env = dotenv_values('.env')
    username = env['MONGO_USER']
    password = env['MONGO_PASSWORD']
    print('mongodb username and password loaded from dotenv')
except:
    print('failed to load dotenv')
    pass


def reduce(x, req):
    vt = bp.find_one({"name": x.name}, {"validTimes": 1, '_id': 0})[
        'validTimes']

    if _requires_update(vt):
        setattr(x, 'validTimes', vt)
        req.append(x)
    else:
        print('database is up to date')
        pass


def _requires_update(vt):
    nowT = datetime.now()
    minT = datetime.strptime(vt[-1], '%Y%m%d-%H%M')
    timeDelta = np.abs((minT - nowT))
    return timeDelta.total_seconds() > 600 or (len(vt) <= 12)


def collect(x):
    url = f"https://mrms.ncep.noaa.gov/data/{x.urlPath}"
    query = "?C=M;O=D"
    page = pd.read_html(url+query)
    prods = np.array(*page)[3:-1]
    # ? flattens the df column as a 1-d array
    files = prods[:, [0]].flatten()

    for file in files:
        # ? find string time
        strtime = re.search(r"(?!.*_)(.*)(?=.grib2.gz)", file).group()
        new_vt = datetime.strptime(strtime, '%Y%m%d-%H%M%S')

        if (new_vt.minute % 10 == 0):
            setattr(x, 'validtime', f'{strtime[:-2]}')
            setattr(x, 'file', file)
            break

    if x.validTimes[-1] == x.validtime:
        # setattr(x, 'state', False)
        print('new data unavaliable')
        pass
    else:
        # setattr(x, 'state', True)
        setattr(x, 'filename', f'{x.name}-{x.validtime}')
        setattr(x, 'filepath', f'tmp/raw/{x.file}')
        request.urlretrieve(url+file, x.filepath)
        return x


def download_allprobsevere():
    url = 'https://mrms.ncep.noaa.gov/data/ProbSevere/PROBSEVERE/'
    query = "?C=M;O=D"
    page = pd.read_html(url+query)
    prods = np.array(*page)[2:-1]
    file_names = prods[:, [0]].flatten()

    for fn in file_names:
        path = f'data/{fn}'
        file_url = f'{url}{fn}'
        print(f'saving file to \n {path}')
        request.urlretrieve(file_url, path)


DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)
ZOOM = 5

#!#############|  MONGODB   |#################
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


def process(x, zoom=5):

    dpi = np.multiply(150, zoom)

    # img_source = f'{x.filename}-{zoom}'

    # ? set zxy params via the TileNames Class
    tn = TileNames(latrange=DESIRED_LATRANGE,
                   lonrange=DESIRED_LONRANGE,
                   zooms=zoom, verbose=False)

    # ? wrapper for the MMM-py MosaicDisplay class
    display = Mosaic(gribfile=x.filepath, dpi=dpi, work_dir='tmp/img/',
                     latrange=tn.latrange, lonrange=tn.lonrange)

    # ? wrapper for the MMM-py plot_horiz function
    file = display.render(filename=f'{x.filename}-{zoom}')

    # ? using the provided tile names slice the Mosaic image into a slippy map directory

    display.crop(file=file, tmp='tmp/data/', product=x.name,
                 validtime=x.validtime, zoom=zoom, tile_names=tn)
    plt.close('all')

# ?______________________________________________________

# * --------------------(    SAVE    )--------------------
# ?______________________________________________________


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
