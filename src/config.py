"""
This module:
- sets up the logger
- defines file paths
- imports the .env file
- defines start and end date for evaluations
- defines parameters used in the evaluations
- defines the DB connection type
- selects which sensor types to evaluate

Import this module in any other modules and in the beginning of each notebook.

.. note::
    The root logger is setup to log to a file and to the console. The console 
    handler is set to INFO level, which is convenient, because instead of using 
    print() to display information, you can use logger.info() and see the 
    output in the console and in the file. The file is helpful for longer outputs 
    and back tracking.
"""

import sys
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import find_dotenv, load_dotenv


### define paths 

# Project root directory (xxx/SmartBuilding)
project_dir = Path(__file__).resolve().parents[1]

# data path for the raw data as downloaded from the DB
data_raw_dir = project_dir / "data" / "raw"

# data path for the processed data
data_processed_dir = project_dir / "data" / "processed"

# data path for the reports
reports_dir = project_dir / "reports"

# data path for the modelling results, e.g. SARIMAX
model_dir = project_dir / "models"





### Setup logging

# The root logger is setup to log to a file and to the console. The console handler is set to INFO level,
# which is convenient because instead of using print() to display information, you can use logger.info() and
# see the output in the console and in the file. The file is helpful for longer outputs.


# Get the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO) # logging.INFO



# Remove existing handlers to avoid output to console
root_logger.handlers = []

# Create file formatter
file_formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s- %(message)s')
file_formatter.default_time_format = '%Y%m%d %H:%M:%S'

# Create handler for file logging
log_file_path = project_dir / 'logs' / 'SmartBuilding.log'
file_handler = RotatingFileHandler(log_file_path, maxBytes=3*1024*1024, backupCount=5)
file_handler.setLevel(logging.NOTSET)
file_handler.setFormatter(file_formatter)

# Create console formatter
console_formatter = logging.Formatter('%(message)s')

# Create handler for console logging
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# Add handler to the logger
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# log start time
root_logger.info('config==========================================')


# get logger for this file
logger = logging.getLogger("config")
logger.info('running config.py')

# log paths
logger.info(f"project dir {project_dir}")
logger.info(f"raw data dir {data_raw_dir}")
logger.info(f"processed data dir {data_processed_dir}")
logger.info(f"reports dir {reports_dir}")
logger.info(f"model dir {model_dir}")




### Misc

# load .env file
load_dotenv(find_dotenv())
logger.info(f"loaded .env file from {find_dotenv()}")



### Global parameters

# specify start and end date for all evaluations; use None for no restriction
if True:
    StartDate = "2024-01-01" # the sensor network was setup again around new year
    EndDate = None

else:
    StartDate = None
    EndDate = None

logger.info(f"StartDate: {StartDate}  EndDate: {EndDate}")


# specify how many data points should be used for the evaluation; use None for all data points
NrDataPoints = None #10000 / None
root_logger.info(f"NrDataPoints: {NrDataPoints}")


# select the DB connection type; connection details are defined in .env
# 0 = sqlite3 (connection paramters not yet in .env)
# 1 = MariaDB 
# 2 = MySQL
DBType = 2


# define sensor types to download
sensor_types = ["temperature", "voc", "co2", "humidity", "light", "uv", "pressure"]
logger.info(f"selected sensor_types: {sensor_types}")

# TODO define resampling frequency


root_logger.info('==========================================config')