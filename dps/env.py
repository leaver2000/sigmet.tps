import os
from glob import glob
from time import time

try:
    from dotenv import dotenv_values
    env = dotenv_values('.env')
    username = env['USERNAME']
    password = env['PASSWORD']
    print('mongodb username and password loaded from dotenv')
except:
    print('failed to load dotenv')
    pass

##############|  MONGODB   |#################
url = f"mongodb+srv://{username}:{password}@wild-blue-yonder.jy40m.mongodb.net/database?retryWrites=true&w=majority"


class LocalDirectory:
    root = 'tmp/'
    raw = f'{root}raw/'
    img = f'{root}img/'
    data = f'{root}data/'
    fileservice = glob(os.path.join(f'{data}*/*/*/*/', '*.png'))
    dirs = (raw, img, data)

    def manage(self, instance):
        if instance == 'START':
            for folder in self.dirs:
                os.makedirs(folder, exist_ok=True)
            return time()

        elif instance == 'STOP':
            # rmtree(self.root, ignore_errors=False, onerror=None)
            return time()


ld = LocalDirectory()
