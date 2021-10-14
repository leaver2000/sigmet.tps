import re
import os

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from PIL import Image, ImageChops
# local modules
from dps.mmmpy import MosaicTile, MosaicDisplay
from dps.image_slicer import chop

#*#############|  DEFAULT MAP/IMG SPECS   |#################
DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)
BGCOLOR = '#000000'


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
            r"(?!.*_)(.*)(?=.grib2.gz)", gribfile).group()[:-2]

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

    def _transparent_basemap(self):
        lon_0 = np.mean(self.lonrange)
        lat_0 = np.mean(self.latrange)
        return Basemap(
            projection='merc', lon_0=lon_0, lat_0=lat_0, lat_ts=lat_0,
            llcrnrlat=np.min(self.latrange), urcrnrlat=np.max(self.latrange),
            llcrnrlon=np.min(self.lonrange), urcrnrlon=np.max(self.lonrange),
            resolution=None, area_thresh=None)

    def render(self, filename=None):

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
        return self.imgsource

    def _crop_source(self):
        """
        The MMM-py genrated mosaic is set with a thick black border
        as declared by fig.patch.set_facecolor(BGCOLOR).
        this is used to properly crop the border from the image.
        additionaly all whitespace is made transparent in this function.
        this function is called directly from render_source()  
        """
        # ? crop
        img = Image.open(self.imgsource).convert("RGB")
        bgc = Image.new("RGB", img.size, BGCOLOR)
        diff = ImageChops.difference(img, bgc)
        bbox = diff.getbbox()
        # ? crop convert transparent
        x = np.asarray(img.crop(bbox).convert('RGBA')).copy()
        # ? if bg ==(225,225,225) set transparent
        x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(np.uint8)
        new_img = Image.fromarray(x)
        new_img.save(self.imgsource, "PNG")

    def crop(self, file=None, tmp=None, validtime=None, product=None,  zoom=None, tile_names=None):
        # rows, cols, base _x, and _y are provided by the TileNames class.
        rows = tile_names.rows
        cols = tile_names.cols
        _x, _y = tile_names.baseline

        # tiles are generated based on conditions
        # set by slippy map tile name generator
        tiles = chop(
            filename=file, col=cols, row=rows, save=False)

        for tile in tiles:
            # the baseline x,y value provides an offset to
            # to correct the zxy position for each tile.
            x = _x+tile.row
            y = _y+tile.column
            # setting & making the path
            # print(validtime)
            path = f'{tmp}{product}/{validtime}/{zoom}/{x}'
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
