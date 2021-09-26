import json
import os
import re
import glob
from shutil import rmtree
#   mongodb
# from dotenv import load_dotenv, dotenv_values
from pymongo import MongoClient
from gridfs import GridFS
#   local module
from zxyMRMS import Fetch, render_tiles
from pprint import pprint
# dev_env = load_dotenv()

# if dev_env:
#     conf = dotenv_values('.env')
#     username = conf['USERNAME']
#     password = conf['PASSWORD']
# else:
#     pass
try:
    from dotenv import dotenv_values
    env = dotenv_values('.env')
    username = env['USERNAME']
    password = env['PASSWORD']
    print('using dev env')
except:
    print('could not load dotenv')
    pass

MONGODB_URL = f"mongodb+srv://{username}:{password}@wild-blue-yonder.jy40m.mongodb.net/database?retryWrites=true&w=majority"

##############|  DEFAULT PATH   |#################
TMP_RAW = 'tmp/raw/'
TMP_IMG = 'tmp/img/'
TMP_DATA = 'tmp/data/'
directories = (TMP_RAW, TMP_IMG, TMP_DATA)
##############|  MONGODB CONNECTION   |#################
db = MongoClient(MONGODB_URL)
fs = GridFS(db.nexrad)
##############|  REGEX   |#################
RE_DATA = r"(?<=tmp/data/)(.*)"
GLB_DATA = TMP_DATA+'*/*/*/*/'


def write_img_to_db():
    i = 0
    for filename in glob.glob(os.path.join(GLB_DATA, '*.png')):
        with open(filename, 'rb') as tile:
            name = re.search(RE_DATA, filename).group()
            f = fs.new_file(filename=name)
            try:
                f.write(tile)
                i += 1
            finally:
                f.close()
    print(f'{i} files saved to mongodb')


def make_nexrad_tiles():
    for folder in directories:
        os.makedirs(folder, exist_ok=True)

    with open('baseProducts.json') as prods:
        bp = json.load(prods)
        product = Fetch(base_products=bp, save_loc=TMP_RAW)

        for prod in product.layers:
            print('')
            print('|-- DATA RETREIVED --|')
            print(f"    layerName = {prod['layerName']}")
            print(f"    validTime = {prod['validTime']}")
            print(f"    filePath = {prod['filePath']}\n")

            if prod['dataType'] == 'GRIB2':
                render_tiles(zoom=5,
                             gribpath=prod['filePath'], validtime=prod['validTime'], product=prod['layerName'], dirs=(TMP_IMG, TMP_DATA))

            else:
                print(
                    f'python support for {prod["dataType"] } is not yet implmented')


def remove_expired_images():
    pass


def write_db_directory():
    with open('baseProducts.json') as prods:
        bp = json.load(prods)['layers']
        for layer in bp:
            print(layer)


# write_db_directory()
# with open('tmp/raw/MRMS_PROBSEVERE_20210926_053837.json', 'rb') as prob_severe:
#     # pprint(prob_severe)
#     pd.read_json(prob_severe)


make_nexrad_tiles()
write_img_to_db()
# rmtree('tmp/', ignore_errors=False, onerror=None)
