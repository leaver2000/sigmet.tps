import numpy as np
from dps.withMRMS import TileNames, Mosaic
import matplotlib.pyplot as plt
DESIRED_LATRANGE = (20, 55)
DESIRED_LONRANGE = (-130, -60)
ZOOM = 5


# def process(x):
#     print(x.name, x.filename, x.filepath, x.validtime)


def process(x, zoom=5):

    dpi = np.multiply(150, zoom)

    # img_source = f'{x.filename}-{zoom}'

    # ? set zxy params via the TileNames Class
    tn = TileNames(latrange=DESIRED_LATRANGE,
                   lonrange=DESIRED_LONRANGE,
                   zooms=zoom, verbose=False)

    # ? wrapper for the MMM-py MosaicDisplay class
    display = Mosaic(gribfile=x.filepath, dpi=dpi, work_dir='tmp/img/',
                     latrange=tn.latrange, lonrange=tn.lonrange)

    # ? wrapper for the MMM-py plot_horiz function
    file = display.render(filename=f'{x.filename}-{zoom}')

    # ? using the provided tile names slice the Mosaic image into a slippy map directory

    display.crop(file=file, tmp='tmp/data/', product=x.name,
                 validtime=x.validtime, zoom=zoom, tile_names=tn)
    plt.close('all')
