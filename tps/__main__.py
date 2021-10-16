from types import SimpleNamespace
from shutil import rmtree
import sched
import json
import time
import os
import controller as tps


def start(features):
    paths = ['tmp/data', 'tmp/raw/', 'tmp/img/']
    [os.makedirs(path, exist_ok=True)for path in paths]

    #*----------------------(   reduce   )----------------------*#
    # ? reduce datarequest via database dataset crosschecks

    # crosschecks:
    #     - age of images in mongodb database
    #     - age of gribfile in MRMS dataset
    # updates baseproduct classes /w validTimes attribute
    # appends valid classes to validated_features list
    validated_features = []
    [tps.reduce(feature, validated_features) for feature in features]

    #*----------------------(   collect   )----------------------*#
    # ? collect raw data via the validated_features
    collected_data = [tps.collect(feature) for feature in validated_features]

    #*----------------------(   process   )----------------------*#
    # ? processing of raw grib data into zxy tile format
    #  Reduction, proccesing, & saving are accomplishedin seperate loops.
    #  This enables the multithread proceccesing of images.
    #  Without interfering witih database the database process
    [tps.process(data) if data is not None else None for data in collected_data]

    #*----------------------(   save   )----------------------*#
    # ? Saves images, updates baseproduct, and removes old collections
    [tps.save(data) if data is not None else None for data in collected_data]
    # [save(feature) for feature in validated_features]

    #
    rmtree('tmp/', ignore_errors=False, onerror=None)


# ? load the baseRequest into a type(class)
def load(feature):
    jd = json.dumps(feature)
    return json.loads(jd, object_hook=lambda d: SimpleNamespace(**d))


# ? schedule itterator to run every 8 mins
def ready(sc, request):
    data = []
    s.enter(480, 1, ready, (sc, request))
    [data.append(load(x)) for x in request['request']]
    start(data)


# ? schedule itterator to run every 8 mins
if __name__ == '__main__':
    s = sched.scheduler(time.time, time.sleep)
    s.enter(480, 1, ready, (s, json.load(open('baseRequest.json'))))
    s.run()


def test(request):
    data = []
    [data.append(load(x)) for x in request['request']]
    start(data)


# test(json.load(open('baseRequest.json')))
