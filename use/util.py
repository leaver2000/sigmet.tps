try:
    from dotenv import dotenv_values
    env = dotenv_values('.env')
    username = env['USERNAME']
    password = env['PASSWORD']
    print('using dev env')
except:
    print('failed to load dotenv')
    pass

# REGEX


class Gex:
    grib_vt = r"(?!.*_)(.*)(?=.grib2.gz)"
    json_vt = r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
    data_path = r"(?<=tmp/data/)(.*)"


class Env:
    url = f"mongodb+srv://{username}:{password}@wild-blue-yonder.jy40m.mongodb.net/database?retryWrites=true&w=majority"


cref = dict(layerName='CREF', dataType='GRIB2',
            urlPath='2D/MergedReflectivityQCComposite/', validTimes=list())

vil = dict(layerName='VIL', dataType='GRIB2',
           urlPath='2D/LVL3_HighResVIL/', validTimes=list())

prob = dict(layerName='JSON', dataType='JSON',
            urlPath='ProbSevere/PROBSEVERE/', validTimes=list())


# class BaseProducts:
#     url = "https://mrms.ncep.noaa.gov/data/"
#     query = "?C=M;O=D"
#     features = list([cref, vil, prob])

#     def __init__(self):
#         with open('base_products.json')as base_products:
#             self.request = json.load(base_products)
#             self.features = list()
#             for feature in self.request['request']:
#                 # del feature['dataType']

#                 print(feature)

# pprint(bp)
# self.request = dict(baseUrl=self.baseUrl,
#                     query=self.query, features=self.features)


# base = BaseProducts()
# print(base.request)
