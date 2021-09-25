# builtins
import re
import os
import sys
import threading
import time
#  fetch dependicies
from urllib import request
import pandas as pd
#

import numpy as np
import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import Basemap
from PIL import Image, ImageChops
# local modules
from modules.mmmpy import MosaicTile, MosaicDisplay
from modules.image_slicer import chop

##############|  DEFAULT PATH   |#################
# DEST_PATH = 'data/'
# TMP_DIR = 'tmp/'
# RAWDATA = f'{TMP_DIR}raw/'
##############|  DEFAULT UTIL  |#################
BGCOLOR = '#000000'
RE_GRIB_VALIDTIME = r"(?!.*_)(.*)(?=.grib2.gz)"
RE_JSON_VALIDTIME = r"(?<=MRMS_PROBSEVERE_)(.*)(?=.json)"


##############|  DEFAULT MAP/IMG SPECS   |#################
PROJECTION = 'merc'
# EXAMPLE_GRIB = 'MRMS_MergedReflectivityQCComposite_00.50_20210920-021039.grib2.gz'
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

    def __init__(self, gribfile=None,  work_dir=None,
                 latrange=None, lonrange=None, dpi=None):

        self.gribfile = gribfile
        self.valid_time = re.search(
            RE_GRIB_VALIDTIME, gribfile).group()[:-2]

        # self._proj = 'merc'
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
            labels = [[False, False, False, False], [False, False, False, True]]
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
        """
        The MMM-py genrated mosaic is set with a thick black border
        as declared by fig.patch.set_facecolor(BGCOLOR).
        this is used to properly crop the border from the image.
        additionaly all whitespace is made transparent in this function.
        this function is called directly from render_source()  
        """

        # img_1 = Image.open(self.imgsource)
        img_2 = Image.open(self.imgsource).convert("RGB")
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

    def crop_tiles(self, file=None, tmp=None, validtime=None,product=None,  zoom=None, tile_names=None):
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
            path = f'{tmp}{validtime}/{product}/{zoom}/{x}'
            os.makedirs(path, exist_ok=True)
            # setting & saving the new tile
            filename = f'{path}/{y}.png'
            tile.save(filename)


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
        se_x, se_y = self._make_zxy(self.south_bound+1, self.east_bound+1, z)
        # _zxy2crds() accepts the xyz grid potion and
        # determines the max n,w,s,e crds
        n_crds, w_crds = self._zxy2crds((z, nw_x, nw_y))
        # s_crds, e_crds = self._zxy2crds(np.add((z, se_x, se_y), (0, 1, 1)))
        s_crds, e_crds = self._zxy2crds((z, se_x, se_y))


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






def render_tiles(gribpath=None, gribfile=None, zoom=None,
                 validtime=None, product=None, dirs=None):
 
    img,data = dirs
    gf = gribpath
    vt = validtime
    dpi = np.multiply(150, zoom)
    img_source = f'{product}-{vt}-{zoom}'
   
    # set zxy params via the TileNames Class
    tn = TileNames(latrange=DESIRED_LATRANGE,
                   lonrange=DESIRED_LONRANGE,
                   zooms=zoom, verbose=False)

    # wrapper for the MMM-py MosaicDisplay class
    display = Mosaic(gribfile=gf, dpi=dpi, work_dir=img,
                     latrange=tn.latrange, lonrange=tn.lonrange)

    # wrapper for the MMM-py plot_horiz function
    file = display.render_source(filename=img_source)

    # using the provided tile names slice the Mosaic image into a slippy map directory
    display.crop_tiles(file=file, tmp=data, product=product,
                       validtime=vt, zoom=zoom, tile_names=tn)
    plt.close('all')


class Fetch:
    def __init__(self, base_products=None, save_loc=None):
        self.baseurl = base_products['baseUrl']
        self.layers = base_products['layers']
        self.query = base_products['query']
        self.save_loc = save_loc

        self.grib_data = list()
        self.json_data = list()

        for layer in self.layers:
            if layer['dataType'] == 'GRIB2':
                self._get_grib2(layer)
            if layer['dataType'] == 'JSON':
                self._get_geojson(layer)

    def _get_geojson(self, layer):
        layer_directory = self.baseurl+layer['urlPath']

        page = pd.read_html(layer_directory+self.query)
        layer_product = np.array(page)[0][2][0]


        request.urlretrieve(layer_directory+layer_product,
                            self.save_loc+layer_product)

        validtime = re.search(RE_JSON_VALIDTIME, layer_product).group()[:-2]

        layer['validTime'] = validtime.replace("_", "-")
        layer['filePath'] = self.save_loc+layer_product

    def _validate_time(self, layer_prods=None):


        for prods in layer_prods:
            valid_time = re.search(RE_GRIB_VALIDTIME, prods[0]).group()[:-2]

            if int(valid_time[12:]) == 0:

                return (prods[0], valid_time)
            else:
                print('skipping non-zero interval')
                continue

    def _get_grib2(self, layer):
        layer_directory = self.baseurl+layer['urlPath']  
        page = pd.read_html(layer_directory+self.query) 

        layer_product, validtime = self._validate_time(
            layer_prods=np.array(*page)[3:])

        request.urlretrieve(layer_directory+layer_product,
                            self.save_loc+layer_product)

        layer['validTime'] = validtime
        layer['filePath'] = self.save_loc+layer_product
        self.grib_data.append(self.save_loc+layer_product)
