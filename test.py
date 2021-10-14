# from types import SimpleNamespace
# from shutil import rmtree
# import sched
# import json
# import time
# import os
# from dps.collect import reduce, collect
# from dps.process import process
# from dps.save import save, init_dataset
import pandas as pd
import numpy as np
from urllib import request
import re
import numpy as np
from dps.withMRMS import TileNames, Mosaic
import matplotlib.pyplot as plt
from PIL import Image, ImageChops
DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)
ZOOM = 5
BGCOLOR = '#000000'

# def process(x):
#     print(x.name, x.filename, x.filepath, x.validtime)


def should_loop(rgba, datas):
    newData = []

    def should_be_transparent(r, g, b, a):
        return r == 255 and g == 255 and b == 255 or r == 212 and g == 212 and b == 212

    # print(np.array(datas, dtype=np.uint8))

    for item in datas:

        # print(np.array([item]))
        if should_be_transparent(*item):
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)  # other colours remain unchanged

    rgba.putdata(newData)
    rgba.save('test/loop-altered.png', "PNG")
    # return rgba


def with_numpy(rgba, imgdata):
    white = np.array([[255, 255, 255, 255]], dtype=np.uint8)
    transparent = np.array([255, 255, 255, 0], dtype=np.uint8)
    equal = np.equal(white, imgdata)
    newData = np.where(equal, transparent, imgdata)
    print(dir(imgdata))
    rgba.putpixel(newData)
    rgba.save('test/numpy-altered.png', "PNG")


def with_image1():
    img = Image.open('test/TEST-5.png').convert("RGB")
    bg = Image.new("RGB", img.size, BGCOLOR)
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    new_img = img.crop(bbox)
    rgba = new_img.convert("RGBA")
    datas = rgba.getdata()
    # should_loop(rgba, datas)
    with_numpy(rgba, datas)

    # tran_im.save('test/altered.png', "PNG")
    # print(tran_im)

    # newData = []

    # white = np.array(
    #     [[255, 255, 255, 255]], dtype=np.uint8)
    # # or r == 212 and g == 212 and b == 212
    # grey = np.array([212, 212, 212, 255], dtype=np.uint8)
    # transparent = np.array([255, 255, 255, 0], dtype=np.uint8)

    # imgdata = np.array(datas, dtype=np.uint8)
    # np.equal(white, imgdata)
    # d = np.where(np.equal(white, imgdata),
    #              transparent, imgdata)
    # print(d)
    # im = Image.fromarray(d, mode='RGBA')
    # # rgba.putdata(d)
    # im.save('test/altered.png', "PNG")


def with_image():
    img = Image.open('test/TEST-5.png').convert("RGB")
    bg = Image.new("RGB", img.size, BGCOLOR)
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    x = np.asarray(img.crop(bbox).convert('RGBA')).copy()
    x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(np.uint8)
    new_img = Image.fromarray(x)
    new_img.save('test/altered.png', "PNG")


# with_image()


def process(zoom=5):

    dpi = np.multiply(150, zoom)

    # img_source = f'{x.filename}-{zoom}'

    # ? set zxy params via the TileNames Class
    tn = TileNames(latrange=DESIRED_LATRANGE,
                   lonrange=DESIRED_LONRANGE,
                   zooms=zoom, verbose=False)

    # ? wrapper for the MMM-py MosaicDisplay class
    gf = 'test/MRMS_MergedReflectivityQCComposite_00.50_20211012-164446.grib2.gz'
    display = Mosaic(gribfile=gf, dpi=dpi, work_dir='test/',
                     latrange=tn.latrange, lonrange=tn.lonrange)

    # ? wrapper for the MMM-py plot_horiz function
    file = display.render(filename=f'TEST-{zoom}')

    # ? using the provided tile names slice the Mosaic image into a slippy map directory

    display.crop(file=file, tmp='test/', product='TEST',
                 validtime='test-test-test', zoom=zoom, tile_names=tn)
    plt.close('all')


process()


def collect(x):
    url = f"https://mrms.ncep.noaa.gov/data/{x.urlPath}"
    query = "?C=M;O=D"
    page = pd.read_html(url+query)
    prods = np.array(*page)[3:-1]
    # ? flattens the df column as a 1-d array
    files = prods[:, [0]].flatten()

    print(files[0])
    file = files[0]
    request.urlretrieve(url+file, f'test/{file}')


class DataSet:
    urlPath = '2D/MergedReflectivityQCComposite/'


# collect(DataSet())
