import numpy as np
from dps.withMRMS import TileNames, Mosaic
import matplotlib.pyplot as plt
DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)

def process(product,validtime,gribpath):
    print(product,validtime,gribpath)
    _process_tiles(product=product,validtime=validtime, gribpath=gribpath,zoom=5)



def _process_tiles(gribpath=None, zoom=None,
                    validtime=None, product=None):

    dpi = np.multiply(150, zoom)
    print(dpi)
    img_source = f'{product}-{validtime}-{zoom}'

#     # set zxy params via the TileNames Class
    tn = TileNames(latrange=DESIRED_LATRANGE,
                    lonrange=DESIRED_LONRANGE,
                    zooms=zoom, verbose=False)

#     # wrapper for the MMM-py MosaicDisplay class
    display = Mosaic(gribfile=gribpath, dpi=dpi, work_dir='tmp/img/',
                        latrange=tn.latrange, lonrange=tn.lonrange)

#     # wrapper for the MMM-py plot_horiz function
    file = display.render_source(filename=img_source)

#     # using the provided tile names slice the Mosaic image into a slippy map directory

    display.crop_tiles(file=file, tmp='tmp/data/', product=product,
                        validtime=validtime, zoom=zoom, tile_names=tn)
    plt.close('all')