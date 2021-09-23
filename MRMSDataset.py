# builtins
import re
import os
import sys
import threading
import time
from shutil import rmtree
from urllib import request
# libs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from PIL import Image, ImageChops
from math import floor
# local modules
from modules.mmmpy import MosaicTile, MosaicDisplay
from modules.image_slicer import chop
# from modules import mmmpy
# MosaicTile, MosaicDisplay = mmmpy

print('hello from MRMSdataset')
# Basemap = basemap.Basemap
##############|  DEFAULT PATH   |#################
DEST_PATH = 'data/'
WORK_PATH = 'tmp/'
RAWDATA = f'{WORK_PATH}raw/'
##############|  DEFAULT UTIL  |#################
BGCOLOR = '#000000'
RE_GRIB_VALIDTIME = r"(?!.*_)(.*)(?=.grib2.gz)"
RE_JSON_VALIDTIME = r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
##############|  DEFAULT REQUEST  |#################
BASE_URL = 'https://mrms.ncep.noaa.gov/data/'
BASE_PRODUCTS = [{
    'dataType': 'GRIB2',
    'layerName': 'CREF',
    'urlPath': '2D/MergedReflectivityQCComposite/',
    'latest': True

}, {
    'dataType': 'GRIB2',
    'layerName': 'VIL',
    'urlPath': '2D/LVL3_HighResVIL/',
    'latest': True

}, {
    'dataType': 'GeoJSON',
    'layerName': 'probSevere',
    'urlPath': 'ProbSevere/PROBSEVERE/',
    'query': '?C=M;O=D',
    'latest': True
}]
##############|  DEFAULT MAP/IMG SPECS   |#################
PROJECTION = 'merc'
EXAMPLE_GRIB = 'MRMS_MergedReflectivityQCComposite_00.50_20210920-021039.grib2.gz'
DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)
DESIRED_ZOOM = 5


class Mosaic:
    """
    GenerateMosaic is a wrapper for the MMM-py library
    --------

    All of the grib2 rendering tasks are accomplished by the MMM-py module.
    https://github.com/nasa/MMM-Py a big thanks to tjlang for his work on it.

    The primary intent of this class is to use the grib2 data provided by the
    NSSL, and render the data into 256x256 tile squares for use in a ZXY slippy tile format.

    """

    def __init__(self, gribfile=None,  work_dir=WORK_PATH,
                 latrange=None, lonrange=None, dpi=None):

        # if type(gribfile) is str:
        # self.gribfile = gribfile
        #     # regex = r"(?!.*_)(.*)(?=.grib2.gz)"
        # self.valid_time = re.search(RE_GRIB_VALIDTIME, gribfile).group()[:-2]

        # # elif type(gribfile) is dict:
        # #     self.gribfile = gribfile['filePath']

        # self._proj = 'merc'
        # self._work_dir = work_dir
        # self.latrange = latrange
        # self.lonrange = lonrange
        # self.dpi = dpi

        gribIsValid = bool(re.search(r'(?=\.grib2.gz$)', gribfile))

        if gribIsValid:
            self.gribfile = gribfile
            # regex = r"(?!.*_)(.*)(?=.grib2.gz)"
            self.valid_time = re.search(
                RE_GRIB_VALIDTIME, gribfile).group()[:-2]

            # elif type(gribfile) is dict:
            #     self.gribfile = gribfile['filePath']

            self._proj = 'merc'
            self._work_dir = work_dir
            self.latrange = latrange
            self.lonrange = lonrange
            self.dpi = dpi
            try:
                self.display = MosaicDisplay(MosaicTile(filename=self.gribfile,
                                                        latrange=self.latrange,
                                                        lonrange=self.lonrange,
                                                        verbose=False))
            except:
                print('there was an error while attemping to render grib the file')
        else:
            print('a valid .grib2.gz file must be provided')

    def _transparent_basemap(self, options=None):

        lon_0 = np.mean(self.lonrange)
        lat_0 = np.mean(self.latrange)

        return Basemap(
            projection='merc', lon_0=lon_0, lat_0=lat_0, lat_ts=lat_0,
            llcrnrlat=np.min(self.latrange), urcrnrlat=np.max(self.latrange),
            llcrnrlon=np.min(self.lonrange), urcrnrlon=np.max(self.lonrange),
            resolution=None, area_thresh=None)

    def show_slippy_grid(self, basemap=None, tiles=None, show_labels=False):
        if show_labels:
            labels = [[False, True, True, False], [True, False, False, True]]
        else:
            labels = [[False, False, False, False],
                      [False, False, False, False]]
        for i, row in enumerate(tiles):
            if i == 0:
                for col in tiles[row]['crds']:
                    basemap.drawparallels((col[0][0], 0, 0), labels=labels[0])
            verts = tiles[row]['crds'][0][0][1]

            try:
                basemap.drawmeridians((verts, 0, 0), labels=labels[1])
            except:
                break

    def render_source(self, filename=None):

        m = self._transparent_basemap()
        self.imgsource = f'{self._work_dir}{filename}.png'
        fig = plt.figure(dpi=self.dpi)
        fig.patch.set_facecolor(BGCOLOR)
        ax = plt.axes()

        self.display.plot_horiz(basemap=m, return_flag=True, fig=fig, ax=ax,
                                latrange=self.latrange, lonrange=self.lonrange, title='',
                                colorbar_flag=False, show_grid=False, verbose=False)

        plt.savefig(self.imgsource, facecolor=fig.get_facecolor(),
                    transparent=False, dpi=self.dpi)

        self._crop_source()
        print(f'source image saved at {self.imgsource}\n')
        return self.imgsource

    def _crop_source(self):
        '''
        The MMM-py genrated mosaic is set with a thick black border
        as declared by fig.patch.set_facecolor(BGCOLOR).
        this is used to properly crop the border from the image.
        additionaly all whitespace is made transparent in this function.
        this function is called directly from render_source()      
        '''

        img_1 = Image.open(self.imgsource)
        img_2 = img_1.convert("RGB")
        bg = Image.new("RGB", img_2.size, BGCOLOR)
        diff = ImageChops.difference(img_2, bg)
        bbox = diff.getbbox()
        new_img = img_2.crop(bbox)
        rgba = new_img.convert("RGBA")
        datas = rgba.getdata()
        newData = []

        def should_be_transparent(r, g, b, a):
            return r == 255 and g == 255 and b == 255 or r == 212 and g == 212 and b == 212

        for item in datas:
            if should_be_transparent(*item):
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)  # other colours remain unchanged

        rgba.putdata(newData)
        rgba.save(self.imgsource, "PNG")
        return rgba

    def crop_tiles(self, file=None, product=None, validtime=None, zoom=None, tile_names=None):
        # rows, cols, base _x, and _y are provided by the TileNames class.
        rows = tile_names.rows
        cols = tile_names.cols
        _x, _y = tile_names.baseline
        # tiles are generated based on conditions set by
        # slippy map tile name generator
        # tiles = image_slicer.slice(
        #     filename=file, col=cols, row=rows, save=False)
        tiles = chop(
            filename=file, col=cols, row=rows, save=False)
        for tile in tiles:
            # the baseline x,y value provides an offset to
            # to correct the zxy position for each tile.
            x = _x+tile.row
            y = _y+tile.column
            # setting & making the path
            path = f'{DEST_PATH}{product}/{validtime}/{zoom}/{x}'
            os.makedirs(path, exist_ok=True)
            # setting & saving the new tile
            filename = f'{path}/{y}.png'
            tile.save(filename)

    def slice(
        filename,
        number_tiles=None,
        col=None,
        row=None,
        save=True,
        DecompressionBombWarning=True,
    ):
        """
        Split an image into a specified number of tiles.
        Args:
        filename (str):  The filename of the image to split.
        number_tiles (int):  The number of tiles required.
        Kwargs:
        save (bool): Whether or not to save tiles to disk.
        DecompressionBombWarning (bool): Whether to suppress
        Pillow DecompressionBombWarning
        Returns:
            Tuple of :class:`Tile` instances.
        """
        if DecompressionBombWarning is False:
            Image.MAX_IMAGE_PIXELS = None

        im = Image.open(filename)
        im_w, im_h = im.size

        columns = 0
        rows = 0
        if number_tiles:
            validate_image(im, number_tiles)
            columns, rows = calc_columns_rows(number_tiles)
        else:
            validate_image_col_row(im, col, row)
            columns = col
            rows = row

        tile_w, tile_h = int(floor(im_w / columns)), int(floor(im_h / rows))

        tiles = []
        number = 1
        # -rows for rounding error.
        for pos_y in range(0, im_h - rows, tile_h):
            for pos_x in range(0, im_w - columns, tile_w):  # as above.
                area = (pos_x, pos_y, pos_x + tile_w, pos_y + tile_h)
                image = im.crop(area)
                position = (int(floor(pos_x / tile_w)) + 1,
                            int(floor(pos_y / tile_h)) + 1)
                coords = (pos_x, pos_y)
                tile = Tile(image, number, position, coords)
                tiles.append(tile)
                number += 1
        if save:
            save_tiles(
                tiles, prefix=get_basename(filename), directory=os.path.dirname(filename)
            )
        return tuple(tiles)


class TileNames:
    """
    usage:

    Translates between lat/long and the slippy-map tile numbering scheme.
    The generate() method accepts fixed lat/lon range and itterates over
    a zoom array.  The returned object contians the tiles XYZ tileName,
    and the tiles lat/lon grid range.

    makeXY && num2deg were sourced from the openstreets map wiki
    https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
    ----------------------------------------------------------------

    use case:
    you have a image high resolution image you want to crop into
    many smaller tiles for a XYZ.

    ----------------------------------------------------------------

    example:

    crds_range = np.array([[20, 55.0], [-130.0, -60.0]])
    zoom_list = ([4])
    slpy = Slippy(fixed_range=crds_range, zoom_list=zoom_list)
    tile_objects = slpy.tiles
    print(slpy.tiles)

    >>>{'zoomLevel': 2, 'tileName': [(2, 0, 1)], 'tileRange': [(0.0, -180.0, 66.51326044311186, -90.0)]}, {'zoomLevel': 3, .....

    for scale in slpy.tiles:
        UseTileObjectToChopUpAnIMGorSomething(scale)

    """

    def __init__(self, latrange=None, lonrange=None, zooms=None, verbose=False):
        self.verbose = verbose
        # lat_range, lon_range = crds_range
        self.south_bound, self.north_bound,  = latrange
        self.west_bound, self.east_bound = lonrange
        self.zooms = zooms
        self.latrange = list()
        self.lonrange = list()

        if lonrange is None or zooms is None:
            print('a lat/lng range was not specified')
            return None

        elif type(zooms) is list:
            arr = list()
            for z in zooms:
                zoom_dict = self._make_tile_dict(z)
                arr.append(zoom_dict)
            self.tiles = arr
            return None

        elif type(zooms) is int:
            # self._make_tile_dict(zoom_list)
            self.tiles = self._make_tile_dict(zooms)
            return None

        else:
            print('unknown error')

    def _make_tile_dict(self, z):

        x_range, y_range = self._set_range(z)
        # print(np.diff(x_range), np.diff(y_range))
        self.cols = np.diff(x_range)[0]
        self.rows = np.diff(y_range)[0]
        tile_dict = dict()
        self.zxy = list()
        for x in range(*x_range):
            zxy_col = list()
            crds_col = list()

            for y in range(*y_range):

                nw_crds = self._zxy2crds((z, x, y))
                se_crds = self._zxy2crds(np.add((z, x, y), (0, 1, 1)))
                zxy_col.append((z, x, y))
                # zxy_row.append((z, x, y+1))
                crds_col.append((nw_crds, se_crds))
                self.zxy.append((z, x, y))

            tile_dict[f'col_{str(x)}'] = dict(zxy=zxy_col, crds=crds_col)

        return tile_dict

    def _set_range(self, z):
        # range calls upon _make_zxy() to return the 2 outter most map vertex points.
        # By default _make_zxy() returns the north-western vertex for the provided crds.
        nw_x, nw_y = self._make_zxy(
            self.north_bound, self.west_bound, z)
        # By passing the (south_bounds,east_bounds) and adding (1,1) _make_zxy()
        # the returned value is the south eastern most point on the map.
        # se_x, se_y = np.add(self._make_zxy(
        #     self.south_bound, self.east_bound, z), (1, 1, 0))
        se_x, se_y = self._make_zxy(self.south_bound+1, self.east_bound+1, z)
        # _zxy2crds() accepts the xyz grid potion and
        # determines the max n,w,s,e crds
        n_crds, w_crds = self._zxy2crds((z, nw_x, nw_y))
        # s_crds, e_crds = self._zxy2crds(np.add((z, se_x, se_y), (0, 1, 1)))
        s_crds, e_crds = self._zxy2crds((z, se_x, se_y))
        if self.verbose:
            self._diag(n_crds, s_crds, w_crds, e_crds,
                       z, nw_x, nw_y, se_x, se_y)

        # external binds in various formats
        self.n_crds = n_crds
        self.w_crds = w_crds
        self.s_crds = s_crds
        self.e_crds = e_crds
        self.sw_crds = (s_crds, w_crds)
        self.ne_crds = (n_crds, e_crds)
        self.latrange.append((n_crds, s_crds))
        self.lonrange.append((w_crds, e_crds))
        self.nw_zxy = (z, nw_x, nw_y)
        self.se_zxy = (z, se_x, se_y)
        # baseline IMPORTANT
        self.baseline = (nw_x-1, nw_y-1)

        return np.array([(nw_x, se_x), (nw_y, se_y)])

    def _make_zxy(self, lat_deg, lon_deg, zoom):

        lat_rad = np.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * n)
        return (xtile, ytile)

    def _zxy2crds(self, zxy):
        z, x, y = zxy
        n = 2.0 ** z
        lon_deg = x / n * 360.0 - 180.0
        lat_rad = np.arctan(np.sinh(np.pi * (1 - 2 * y / n)))
        lat_deg = np.degrees(lat_rad)
        return (lat_deg, lon_deg)

    def list(self, options=None):

        if options is None:
            print(f"instance.n_crds = {self.n_crds} \n")
            print(f"instance.w_crds = {self.w_crds} \n")
            print(f"instance.s_crds = {self.s_crds} \n")
            print(f"instance.e_crds = {self.e_crds} \n")
            print(f"instance.sw_crds = {self.sw_crds} \n")
            print(f"instance.ne_crds = {self.ne_crds} \n")
            print(f"instance.latrange = {self.latrange} \n")
            print(f"instance.lonrange = {self.lonrange} \n")
            print(f"instance.nw_zxy = {self.nw_zxy} \n")
            print(f"instance.se_zxy = {self.se_zxy} \n")
            print("for zoom_level in self.tiles: \n")
            for zoom_level in self.tiles:
                print(f"    zoom_level = {zoom_level} \n")

    def _diag(self, n_crds, s_crds, w_crds, e_crds, z, nw_x, nw_y, se_x, se_y):
        spacer = '                                 '
        print(f'\n      ||  generating vertex range for zoom level {z}  || \n',
              f'\n   nw_crds:     {spacer}      ne_crds',

              f'\n{(np.round(n_crds,4),np.round(w_crds,4))}{spacer}{(np.round(n_crds,4),np.round(e_crds,4))}',
              '\n    _________________________________________________________',
              '\n   |                                                         |',
              '\n   |                                                         |',
              '\n   |                                                         |',
              '\n   |                                                         |',
              '\n   |                                                         |',
              '\n   |                                                         |',
              '\n   |                                                         |',
              '\n   |                                                         |',
              '\n   |_________________________________________________________|',
              #   f'\n sw_crds: {(np.round(s_crds,4),np.round(w_crds,4))}                 se_crds: {(np.round(s_crds,4),np.round(e_crds,4))}',
              f'\n   sw_crds:     {spacer}      se_crds',

              f'\n{(np.round(s_crds,4),np.round(w_crds,4))}{spacer}{(np.round(s_crds,4),np.round(e_crds,4))}',
              f'\n\n latrange: {(n_crds,s_crds)}\n lonrange: {(w_crds,e_crds)}'

              f'\n\n nw_zxy: {(z,nw_x,nw_y)} se_zxy: {(z,se_x,se_y)}\n')


class Fetch:
    """
    # FetchData

    Get current data serves as the local data manager for the GenerateMosaic Class.  GCD's role is to access data from
    the NSSL dataset.  Passing an list of objects with the path to the layer directory and a layername. GCD will retreive
    and store the raw data locally for later processing. GCD Returns an object with information specific to the raw data
    that was retreived, such as the validTime and localPath directory to the raw data.

    This list can then be passed to the GenerateMosaic():

    class where the information will be degribed and processed into a WMTS friendly format.

    example usage....

    data = GetCurrentData(LAYERS)

    GenerateMosaic(data.layers)

    -----------------------------------------------------------------------------


    """

    def __init__(self, layers=BASE_PRODUCTS):

        os.makedirs(RAWDATA, exist_ok=True)
        self.baseurl = BASE_URL
        self.layers = layers
        self.grib_data = list()
        self.json_data = list()

        try:
            for layer in self.layers:
                try:
                    if layer['dataType'] == 'GRIB2':
                        self._get_grib2(layer)
                    if layer['dataType'] == 'GeoJSON':
                        self._get_geojson(layer)

                    # self._retreive_data(layer)
                except:
                    print('there was an error in the data request for the layer',
                          layer['layerName'])

        except:
            print('there was an error in the initial layer request')

    def _get_geojson(self, layer):
        layer_directory = self.baseurl+layer['urlPath']
        # page = pd.read_html(layer_directory+layer['query'])?C=M;O=D
        page = pd.read_html(f'{layer_directory}?C=M;O=D')
        layer_product = np.array(page)[0][2][0]

        # print(layer_directory+layer_product)
        request.urlretrieve(layer_directory+layer_product,
                            RAWDATA+layer_product)
        # regex = r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
        # RE_JSON_VALIDTIME=r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"
        validtime = re.search(RE_JSON_VALIDTIME, layer_product).group()[:-2]

        layer['validTime'] = validtime.replace("_", "-")
        layer['filePath'] = RAWDATA+layer_product

    def _validate_time(self, layer_prods=None):

        # regex = r"(?!.*_)(.*)(?=.grib2.gz)"
        for prods in layer_prods:
            valid_time = re.search(RE_GRIB_VALIDTIME, prods[0]).group()[:-2]

            if int(valid_time[12:]) == 0:

                return (prods[0], valid_time)
            else:
                print('skipping non-zero interval')
                continue

    def _get_grib2(self, layer):
        layer_directory = self.baseurl+layer['urlPath']  # +layer['query']
        page = pd.read_html(f'{layer_directory}?C=M;O=D')  # ?C=M;O=D

        layer_product, validtime = self._validate_time(
            layer_prods=np.array(*page)[3:])

        request.urlretrieve(layer_directory+layer_product,
                            RAWDATA+layer_product)

        layer['validTime'] = validtime
        layer['filePath'] = RAWDATA+layer_product
        self.grib_data.append(RAWDATA+layer_product)


def render_tiles(gribpath=None, gribfile=EXAMPLE_GRIB,
                 validtime=None, product=None):

    if gribpath is None:
        gf = f'{RAWDATA}{gribfile}'
    elif gribpath is not None:
        gf = gribpath
    if validtime is None:
        vt = re.search(RE_GRIB_VALIDTIME, gribfile).group()[:-2]
    elif validtime is not None:
        vt = validtime

    zoom = DESIRED_ZOOM
    # for zoom in DESIRED_ZOOMS:

    dpi = np.multiply(150, zoom)
    img_source = f'{product}-{vt}-{zoom}'
    # _diag(img_source, product, vt, zoom, dpi)

    # set zxy params via the TileNames Class
    tn = TileNames(latrange=DESIRED_LATRANGE,
                   lonrange=DESIRED_LONRANGE,
                   zooms=zoom, verbose=False)

    # wrapper for the MMM-py MosaicDisplay class
    display = Mosaic(gribfile=gf, dpi=dpi,  work_dir=WORK_PATH,
                     latrange=tn.latrange, lonrange=tn.lonrange)

    # wrapper for the MMM-py plot_horiz function
    file = display.render_source(filename=img_source)

    # using the provided tile names slice the Mosaic image into a slippy map directory
    display.crop_tiles(file=file, product=product,
                       validtime=vt, zoom=zoom, tile_names=tn)
    plt.close('all')


def call_tiles():
    product = Fetch(layers=BASE_PRODUCTS)

    for prod in product.layers:
        print('')
        print('|-- DATA RETREIVED --|')
        print(f"    layerName = {prod['layerName']}")
        print(f"    validTime = {prod['validTime']}")
        print(f"    filePath = {prod['filePath']}\n")

        if prod['dataType'] == 'GRIB2':
            render_tiles(
                gribpath=prod['filePath'], validtime=prod['validTime'], product=prod['layerName'])

        else:
            print(
                f'python support for {prod["dataType"] } is not yet implmented')

    rmtree(WORK_PATH)


call_tiles()

# start_time = time.time()
# call_tiles()
# count = 1
# while not threading.Event().wait(600):
#     call_tiles()
#     elapsed_time = time.time() - start_time
#     days = 0
#     if elapsed_time >= 86400:
#         days = int(elapsed_time / 86400)
#     elapsed = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
#     count += 1
#     if days == 0:
#         print(f"The module has been running for {elapsed} hours")

#     else:
#         print(f"The module has been running for {days} days & {elapsed} hours")

#     print(f"The module has executed {count} times.\n")
