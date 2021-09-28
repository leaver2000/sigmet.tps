import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from modules.withMRMS import TileNames, Mosaic, ProbSevere

DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)


def process_tiles(gribpath=None, gribfile=None, zoom=None,
                  validtime=None, product=None, dirs=None):

    img, data = dirs
    dpi = np.multiply(150, zoom)
    img_source = f'{product}-{validtime}-{zoom}'

    # set zxy params via the TileNames Class
    tn = TileNames(latrange=DESIRED_LATRANGE,
                   lonrange=DESIRED_LONRANGE,
                   zooms=zoom, verbose=False)

    # wrapper for the MMM-py MosaicDisplay class
    display = Mosaic(gribfile=gribpath, dpi=dpi, work_dir=img,
                     latrange=tn.latrange, lonrange=tn.lonrange)

    # wrapper for the MMM-py plot_horiz function
    file = display.render_source(filename=img_source)

    # using the provided tile names slice the Mosaic image into a slippy map directory
    display.crop_tiles(file=file, tmp=data, product=product,
                       validtime=validtime, zoom=zoom, tile_names=tn)
    plt.close('all')


def process_probsevere(filepath=None):
    if filepath is None:
        print('a file path was not provided')
    else:
        with open(filepath, 'rb') as f:
            fc = np.array(pd.read_json(f))
            return ProbSevere(feature_collection=fc)
