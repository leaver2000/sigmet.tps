import numpy as np
import pandas as pd
import re
from urllib import request
# from types import SimpleNamespace
# import json
from dps.save import bp
from datetime import datetime


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
