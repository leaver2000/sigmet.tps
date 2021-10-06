
import os
from shutil import rmtree
from use.baseproducts import BaseProducts
from use.router import Router
import time
# local data manager

##############|  LocalDirectory   |#################


class LocalDirectory:
    root = 'tmp/'
    raw = f'{root}raw/'
    img = f'{root}img/'
    data = f'{root}data/'
    dirs = (raw, img, data)
    # def tree(self):
    #     return (self.raw, self.img, self.data)

    def manage(self, instance):
        if instance == 'START':
            for folder in self.dirs:
                os.makedirs(folder, exist_ok=True)
            return time.time()

        elif instance == 'STOP':
            rmtree(self.root, ignore_errors=False, onerror=None)
            return time.time()


def controller(verbose=False):
    """
    # Steps

    # collect:
        Opens baseProducts.json and pulls data from the MRMS Dataset using the Fetch module.

    # prep:
        prep itterates through the dataset and calls the aplicable functions to process the data.  Additional

    # post:

    # update

    """
    #####################|  PROBSEVERE INSTANCE   |#####################
    # First an EXSISTING instance of ProbSevere is passed into a NEW instance BaseProducts.
    #
    # BaseProducts manages its own state without resetting the ProbSevere state.
    #
    # ProbSevere returns GeoJson to BaseProducts which is then saved to MONGO DB
    # Each new instance of BaseProducts removes the existing GeoJSON from memory.
    # While ProbSevere maintains its memory outside of the loop for compairsons
    # to previous itteratings of ndarrays.
    #
    ########################################################

    ld = LocalDirectory()
    bp = BaseProducts(dirs=ld.dirs)
    # maintain_tmp_tree creates a new tmp tree dir for intermediate processing
    initial_timer = ld.manage('START')
    #####################|  COLLECT   |#####################
    # call the baseproducts fetch api to collect the raw data
    ########################################################
    if verbose:
        intermediate_timer = time.time()

    bp.collect()

    if verbose:
        print(f'data collection accomplished in: \
                {round(time.time() - intermediate_timer)} seconds')

    ######################|  PREPARE & PROCESS  |#################
    # call the baseproducts prepare_and_process function.
    # this stage relies heavily on the withMRMS module and MMM-py
    # to handle the data processing required to render the png images.
    ###############################################################
        intermediate_timer = time.time()

    bp.process()

    if verbose:
        print(f'data processing accomplished in: \
                {round(time.time() - intermediate_timer)} seconds')

        intermediate_timer = time.time()
    #######################|  COMMIT & POST   |####################
    #
    ###############################################################

    route = Router(bp.features)
    route.probsevere(bp.probsevere)
    route.gridfs(bp.fileservice)

    route.close()
    if verbose:
        print(f'data writing took \
                {round(time.time() - intermediate_timer)} seconds')

    # once the database is updated maintain_tmp_tree then removes tmp/ and all associated files.
    end_timer = ld.manage('STOP')
    if verbose:
        print(f'total processing accomplished in: \
                {round(end_timer - initial_timer)} seconds')


# class Name:
#     first = 'billy'


# print(Name.first)
controller(verbose=True)
