from use.util import Gex, Env
from pymongo import MongoClient
from gridfs import GridFS
import re
##############|  MONGODB   |#################
client = MongoClient(Env.url)

##############|  Database   |#################
db = client.sigmet
# ?____________________________________________

# *          DATABASE COLLECTIONS
# ?____________________________________________
fs = GridFS(db)  # ? FILESERVER COLLECTION
ps = db.probSevere  # ? PROBSEVERE COLLECTION
bp = db.baseProducts  # ? PRODUCT DIRECTORY METADATA

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


def switch(collection):
    try:
        return {
            # 'BASEREQUEST': br,
            'BASEPRODUCT': bp,
            'PROBSEVERE': ps,
        }[collection]
    except:
        print('an invalid collection was used')
        return None


def update_collection(data, collection=str):
    if collection is not None:
        col = switch(collection)
        print(data)
        # col.update_someStuff()
        return
    else:
        print('a collection must be specified')


class Update:
    def __init__(self, data):
        for d in data:
            del d['urlPath']
            del d['filePath']

        self.data = data
        return None

    def gridfs(self, data):
        for path in data:
            with open(path, 'rb') as fp:
                filename = re.search(r"(?<=tmp/data/)(.*)", fp.name).group()
                f = fs.new_file(filename=filename)
                try:
                    f.write(data)
                finally:
                    f.close()

    def probsevere(self, data):
        ps.insert_one(data)

    def close(self):
        bp.insert_many(self.data)


def insert_many(data, collection=None):
    col = switch(collection)
    return col.insert_many(data)


def read_all(collection=None, query=None):
    """
    #### Connects to mongo db to retrun the entire colleciton
    currently supported to return the following arguments:
    - BASEPRODUCTS
    - PROBSEVERE
    """
    col = switch(collection)
    data = list()
    for item in col.find():
        data.append(item)
    return data

    # if collection == 'BASEPRODUCTS' or collection == 'PROBSEVERE':
    #     instance = bp if collection == 'BASEPRODUCTS' else ps
    #     data = list()
    #     for item in instance.find():
    #         data.append(item)
    #     return data
    # else:
    #     print('invalid request')
    #     return None


def remove_collection(collection=None):
    if collection == 'BASEPRODUCTS' or collection == 'PROBSEVERE':
        instance = bp if collection == 'BASEPRODUCTS' else ps
        print(f'\n## ALERT ##\nREMOVING ENTIRE COLLECTION: {collection}\n')
        instance.drop()
    else:
        print('invalid request')


# remove_collection(collection='PROBSEVERE')
# def set_collection():
#     try:
#         bp.drop()  # delete a collection
#     except:
#         pass
#     base = BaseProducts()  # reset collection using base_products.json file

#     # update collection with new product information
#     bp.insert_many(base.prodcuts)
