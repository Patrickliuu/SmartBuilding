# This is the main file which runs the data processing pipeline.

import logging
from data import make_dataset
from visualization import visualize

# import config to use global parameters and setup logger
import config


# maybe use click to define command line parameters to run data processing, training, ...
# @click.command()
# @click.option('--stage', default='download', help='Run processing pipeline from this stage on.')
# def main(stage: str):
def main():
    """ Runs the data processing pipeline.
    """

    # Note: The processing pipeline is bluntly implemented. More elegant ways might use
    # Perfect, a Python library for data processing pipelines, Apache Airflow or Luigi.
    
    # get logger
    logger = logging.getLogger(__name__)

    # log start
    logger.info(f'starting pipeline')


    ### this defines the automated analysis pipeline

    # download data from DB
    #make_dataset.download_data()

    # visualize raw data
    #visualize.plot_raw_data()

    # resample data
    #make_dataset.resample_data()

    # visualize processed data
    #visualize.plot_processed_data()

    # compile room data
    #make_dataset.compile_room_data()




if __name__ == '__main__':
    main()