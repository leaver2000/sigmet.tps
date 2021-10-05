
import os
from shutil import rmtree
from use.baseproducts import BaseProducts
from use.mongo import Update
import time


##############|  LocalDirectory   |#################
class LocalDirectory:
    root = 'tmp/'
    raw = f'{root}raw/'
    img = f'{root}img/'
    data = f'{root}data/'
    glob = f'{root}*/*/*/*/'

    def tree(self):
        return (self.raw, self.img, self.data)

    def manage(self, instance):
        if instance == 'START':
            for folder in self.tree():
                os.makedirs(folder, exist_ok=True)
            return time.time()

        elif instance == 'STOP':
            rmtree(self.root, ignore_errors=False, onerror=None)
            return time.time()


##############|  REGEX   |#################
# RE_DATA = r"(?<=tmp/data/)(.*)"


def controller():
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

    bp = BaseProducts()
    ld = LocalDirectory()
    # maintain_tmp_tree creates a new tmp tree dir for intermediate processing
    initial_timer = ld.manage('START')
    #####################|  COLLECT   |#####################
    # call the baseproducts fetch api to collect the raw data
    ########################################################
    intermediate_timer = time.time()
    # bp.collect(save_loc=ld.raw)
    bp.collect(save_loc='tmp/raw/')

    print(f'data collection accomplished in: \
            {round(time.time() - intermediate_timer)} seconds')

    ######################|  PREPARE & PROCESS  |#################
    # call the baseproducts prepare_and_process function.
    # this stage relies heavily on the withMRMS module and MMM-py
    # to handle the data processing required to render the png images.
    ###############################################################
    intermediate_timer = time.time()

    bp.prepare()  # calls to process the probsevere data
    # and returns the updated probsevere feature colleciton
    # bp.prep(prodType='PROBSEVERE')
    # bp.prep(prodType='NEXRAD')

    print(f'data processing accomplished in: \
            {round(time.time() - intermediate_timer)} seconds')

    #######################|  COMMIT & POST   |####################
    #
    ###############################################################
    intermediate_timer = time.time()

    up = Update(bp.features)

    up.probsevere(bp.probsevere)
    up.gridfs(bp.fileservice)

    up.close()

    print(f'data writing took \
            {round(time.time() - intermediate_timer)} seconds')

    # once the database is updated maintain_tmp_tree then removes tmp/ and all associated files.
    end_timer = ld.manage('STOP')
    print(f'total processing accomplished in: \
            {round(end_timer - initial_timer)} seconds')


controller()
