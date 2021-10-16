# TILE PROCESSING SERVER

The tps is a python based module designed to be hosted in the Google Kubernetes Engine (GKE). Its primary purpose is to scrape data from the NSSL MRMS dataset, specifically grib2 radar information.

the baseRequest.json file in the root specifies the initial request information and manages what infromation from the dataset is to be extracted and processed.

The server runs on a schdule to verifiy the information it currently in the managed database against the information that is avaliable in the MRMS dataset.

The server relies heavily on the MMM-py module developed by Timmothy Lang from NASA, to perform the bulk rendering operation.

Prior to making the request to the MMM-py module, DESIRED_LATRANGE, DESIRED_LONRANGE, & ZOOM values are passed to TileNames class.

The TileNames returns an instance for accessing adjusted lat,lons needed to appropriately size, name, and slice the tiles.

the adjusted lat,lons are passed to the Mosaic class wrapper which is a wrapper for the MMM-py module. The wrapper builds the basemap and provides and API to render and crop the image.

As the data sent to the client is required in the zxy tile format, a post processing operation is performed on the rendered images to slice a single image
into several smaller transparent image tiles.

## **main**.py

    __main__ calls functions from the controller.

    controller calls modules

    - reduce
        - pymongo: crosscheck data verification

    - collect
        - scrape dataset: additional data verifcation operations are performed

    - process
        - pass request information to zxyMosaic to render images

    - save
        - pymongo:
            save images to database
            update baseproduct directory
            perform clean up
