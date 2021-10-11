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

def get_gridfs(prod, vt):
    col = f'{prod}-{vt}'
    return[GridFS(db, collection=f'{col}{vm}')for vm in ['.files','.chunks']]

    # files = GridFS(db, collection=f'{col}.files')
    # chunks = GridFS(db, collection=f'{col}.chunks')

    # return (files, chunks)