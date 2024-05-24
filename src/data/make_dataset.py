# Module to download the raw data from the DB and process it for further analysis.

import logging
import pandas as pd

# import config logger initialization
from src import config
import os
from src.data import DB_tools as dbt
from pathlib import Path

# get Logger
logger = logging.getLogger(__name__)

def download_data(start_date="2024-01-01"):
    """ Downloads the data from the DB and saves it in the `config.data_raw_dir`. The saved dataframes 
        contain a single timestamp column (index) and one column for each sensor. If a 
        sensor has no value for a timestamp, the value is NaN (outer merge). 
        The data that is downloaded is defined by `config.sensor_types`. The
        DB connection parameters are defined in `.env`.
    """
    logger.info(f"Starting data download process with start date: {start_date}")
    base_dir = Path.cwd()  # Adjust this if your script is in a different directory structure
    output_dir = base_dir / 'data' / 'raw'
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured existence of directory: {output_dir}")

    sensor_types = dbt.GetSensorTypes()
    sensor_data_dfs = {}  # Dictionary to store dataframes for each sensor type

    for sensor_type in sensor_types['type_name']:
        logger.info(f"Processing {sensor_type} sensors")
        sensor_ids = dbt.GetSensorIdsOfType(sensor_type)

        all_sensor_data = []

        for sensor_id in sensor_ids['sensor_id']:
            sensor_data = dbt.GetTimeSeries(sensor_id, start_date=start_date)
            if sensor_data.empty:
                logger.warning(f"No data found for sensor ID {sensor_id}")
                continue

            sensor_data.set_index('timestamp', inplace=True)
            sensor_data.rename(columns={'value': f'sensor_{sensor_id}'}, inplace=True)
            all_sensor_data.append(sensor_data)

        if all_sensor_data:
            combined_data = pd.concat(all_sensor_data)
            file_path = output_dir / f'{sensor_type}_data.parquet'
            combined_data.to_parquet(file_path)
            logger.info(f"Saved combined data for {sensor_type} to {file_path}")
            sensor_data_dfs[sensor_type] = combined_data
        else:
            sensor_data_dfs[sensor_type] = pd.DataFrame()  # Store an empty DataFrame if no data
            logger.warning(f"No valid data collected for {sensor_type}; creating an empty DataFrame")

    logger.info(f"Saved all sensor data to {file_path}")

    return sensor_data_dfs

def resample_data():
    raise NotImplementedError("Not implemented yet")



if __name__ == '__main__':
    # execute only if run as the entry point into the program

    # download data from DB server
    download_data()

    # resample data
    #resample_data()




