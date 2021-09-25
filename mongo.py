import json
import os
import re
import glob
from shutil import rmtree
##
from pymongo import MongoClient
from gridfs import GridFS
from pprint import pprint
##
from zxyMRMS import Fetch, render_tiles 
# from fetch import Fetch

##############|  DEFAULT PATH   |#################
TMP_RAW='tmp/raw/'
TMP_IMG='tmp/img/'
TMP_DATA='tmp/data/'
directories = (TMP_RAW,TMP_IMG,TMP_DATA)
##############|  REGEX   |#################
RE_DATA = r"(?<=tmp/data/)(.*)"
GLB_DATA = TMP_DATA+'*/*/*/*/'
##############|  MONGODB CONNECTION   |#################
db = MongoClient(
    "mongodb+srv://python_admin:RrbPVfalrHkXMcP5@wild-blue-yonder.jy40m.mongodb.net/database?retryWrites=true&w=majority")
fs = GridFS(db.nexrad)

def write_to_database():
    i = 0
    for filename in glob.glob(os.path.join(GLB_DATA, '*.png')):     
        with open(filename, 'rb') as tile:
            name = re.search(RE_DATA,filename).group()
            f = fs.new_file(filename=name)
            try:
                f.write(tile)
                i+=1
            finally:
                print(f'{i} files saved to mongodb')              
                f.close()

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
                render_tiles( zoom=5,
                    gribpath=prod['filePath'], validtime=prod['validTime'], product=prod['layerName'], dirs=(TMP_IMG,TMP_DATA))

            else:
                print(
                    f'python support for {prod["dataType"] } is not yet implmented')

def read_database_tiles():
    pass

def clean_up_database():
    pass

def clean_up_root():
    pass


make_nexrad_tiles()
write_to_database()
rmtree('tmp/', ignore_errors=False, onerror=None)




