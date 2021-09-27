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
