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
ps = db.probsevere  # ? PROBSEVERE COLLECTION
br = db.base_requests  # ? PRODUCT REQUEST METADATA
bp = db.base_products  # ? PRODUCT DIRECTORY METADATA

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


def switch_collection(collection):
    try:
        return {
            'BASEREQUEST': br,
            'BASEPRODUCT': bp,
            'PROBSEVERE': ps,
        }[collection]
    except:
        print('an invalid collection was used')
        return None


def update_collection(data, collection=None):
    if collection is not None:
        col = switch_collection(collection)
        print(data)
        # col.update_someStuff()
        return
    else:
        print('a collection must be specified')


def post_collection(data, collection=None):

    if collection == 'FILESERVER':
        filename = re.search(r"(?<=tmp/data/)(.*)", data.name).group()
        f = fs.new_file(filename=filename)
        try:
            f.write(data)

        finally:
            f.close()

    elif collection is not None:
        col = switch_collection(collection)
        try:
            ps.insert_one(data)
        except:
            print('there was an error posting the colleciton')

        return
    else:
        print('a collection must be specified')

    # if collection is None:
    #     print('a collection was not specified')

    # elif collection == 'PROBSEVERE':
    #     try:
    #         _id = ps.insert_one(data).inserted_id
    #     except:
    #         print('there was an error posting probSevere data to mongoDB')

    # elif collection == 'FILESERVER':
    #     filename = re.search(r"(?<=tmp/data/)(.*)", data.name).group()
    #     f = fs.new_file(filename=filename)
    #     try:
    #         f.write(data)

    #     finally:
    #         f.close()
    # elif collection == 'test':
    #     print(data)
    # else:
    #     print(
    #         f'there is currently no support for the specified collection: {collection}')


def insert_many(data, collection=None):
    col = switch_collection(collection)
    col.insert_many(data)


def read_all(collection=None, query=None):
    """
    #### Connects to mongo db to retrun the entire colleciton
    currently supported to return the following arguments:
    - BASEPRODUCTS
    - PROBSEVERE
    """
    col = switch_collection(collection)
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
