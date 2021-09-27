from modules.util import Gex, Env
from pymongo import MongoClient, InsertOne
from gridfs import GridFS
import re
##############|  MONGODB   |#################

client = MongoClient(Env.url)
db = client.sigmet
fs = GridFS(db)  # FILESERVER collection
ps = db.probsevere  # PROBSEVERE collection
bp = db.base_products


def post_collection(data, collection=None):
    if collection is None:
        print('a collection was not specified')

    elif collection == 'PROBSEVERE':
        try:
            _id = ps.insert_one(data).inserted_id
        except:
            print('there was an error posting probSevere data to mongoDB')

    elif collection == 'FILESERVER':
        filename = re.search(Gex.data_path, data.name).group()
        f = fs.new_file(filename=filename)
        try:
            f.write(data)

        finally:
            f.close()
    elif collection == 'test':
        print(data)
    else:
        print(
            f'there is currently no support for the specified collection: {collection}')


def update_availiable_products(products):

    print(products)
    pass


def read_database():

    pass


read_database()


def remove_collection():
    pass
