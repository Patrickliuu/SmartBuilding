# Tools to access the DB storing the sensor data.

import os
import logging
import pendulum

import contextlib
import sqlite3
import sqlalchemy

import pandas as pd
from typing import List

# import config to config the logger, load environemt variables, ...
from src import config

### DB connection parameters are now defined in .env and config.py

# get logger
logger = logging.getLogger(__name__)


##### DB connectors

@contextlib.contextmanager
def _open_sqlite():
    """ Connector to the sqlite3 database. """

    conn = sqlite3.connect(db_file)
    try:
        yield conn
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextlib.contextmanager
def _open_mariadb():
    """ Connector to the MariaDB database. """

    # get connection parameters from .env
    DBUser = os.environ.get('MariaDB.User')
    DBPW = os.environ.get('MariaDB.PW')
    DBHost = os.environ.get('MariaDB.Host')
    DBPort = os.environ.get('MariaDB.Port')
    DBName = os.environ.get('MariaDB.DBName')
    logger.debug(f"MariaDB connection parameters: {DBUser} DBPW {DBHost} {DBPort} {DBName}")

    # pandas somehow only supports sqlalchemy and not pymysql and not mysql.connector
    # https://docs.sqlalchemy.org/en/20/dialects/mysql.html#module-sqlalchemy.dialects.mysql.mariadbconnector
    conn = sqlalchemy.create_engine(f"mariadb+mariadbconnector://{DBUser}:{DBPW}@{DBHost}:{DBPort}/{DBName}")

    try:
        yield conn
    except BaseException:
        # conn.rollback()
        raise
    finally:
        conn.dispose()


@contextlib.contextmanager
def _open_mysql():
    """ Connector to the mySQL database. """

    # get connection parameters from .env
    DBUser = os.environ.get('mysql.User')
    DBPW = os.environ.get('mysql.PW')
    DBHost = os.environ.get('mysql.Host')
    # DBPort = os.environ.get('MySql.Port')
    DBName = os.environ.get('mysql.DBName')
    logger.debug(f"MySql connection parameters: {DBUser} DBPW {DBHost} {DBName}")

    # pandas somehow only supports sqlalchemy and not pymysql and not mysql.connector
    # https://docs.sqlalchemy.org/en/20/dialects/mysql.html#module-sqlalchemy.dialects.mysql.pymysql
    conn = sqlalchemy.create_engine(f"mysql+pymysql://{DBUser}:{DBPW}@{DBHost}/{DBName}")

    try:
        yield conn
    except BaseException:
        # conn.rollback()
        raise
    finally:
        conn.dispose()


##### DB queries

def query(sql_query: str, query_args: List[str] = None) -> pd.DataFrame:
    """ Query the database with the specified SQL query and return a dataframe. """

    if config.DBType == 0:
        with _open_sqlite() as conn:
            return pd.read_sql_query(sql_query, conn, params=query_args)
    elif config.DBType == 1:
        with _open_mariadb() as conn:
            return pd.read_sql_query(sql_query, conn, params=query_args)
    elif config.DBType == 2:
        with _open_mysql() as conn:
            return pd.read_sql_query(sql_query, conn, params=query_args)
    else:
        logger.error("DBType not supported")
        raise ValueError("DBType not supported")


def GetSensorId(sensor_name: str) -> pd.DataFrame:
    """ Queries the sensor_id for the specified sensor name. """

    # use a case insensitive collation because the sensor "extensions" are not consistently lowercase
    sql = f"""
    SELECT *
    FROM tblSensor
    WHERE sensor_name COLLATE utf8mb4_general_ci = '{sensor_name}';
    """
    q = query(sql)

    # check if q is empty
    if q.empty:
        logger.error(f"GetSensorId: sensor_name '{sensor_name}' not found in DB")
        raise ValueError(f"GetSensorId: sensor_name '{sensor_name}' not found in DB")

    # return signal_id of the first (and only) row
    return q['sensor_id'][0]


def GetRooms() -> pd.DataFrame:
    """ Queries the rooms that have sensors installed. """

    sql = f"""
    SELECT *
    FROM tblRoom;
    """
    q = query(sql)

    return q


def GetTimeSeries(sensor_id: str, start_date: str = None, end_date: str = None, limit: int = None) -> pd.DataFrame:
    """ Queries the time series of the specified sensor. """

    sql = f"""
    SELECT *
    FROM tblMeasurement
    WHERE sensor_id = {sensor_id}
    """

    if start_date is not None:
        sql += f"""AND date >= '{start_date}'
      """

    if end_date is not None:
        sql += f"""AND date <= '{end_date}'
        """

    sql += f"""ORDER BY date ASC, time ASC
    """

    if limit is not None:
        sql += f"LIMIT {limit};"
    else:
        sql += ";"

    df = query(sql)

    # log results
    logger.debug(f"GetTimeSeries: df head: {df.head()}")
    logger.debug(f"GetTimeSeries: df info: {df.info()}")

    # Combine 'date' and 'time' columns into a single datetime column
    df['date'] = pd.to_datetime(df['date'])
    df['time'] = pd.to_timedelta(df['time'])
    df['timestamp'] = df['date'] + df['time']
    df = df.drop(['date', 'time'], axis=1)

    # make timestamp the index
    # df = df.set_index('timestamp')

    # drop columns that are not needed
    df = df.drop(['sensor_id', 'measurement_id'], axis=1)

    # log results
    logger.debug(f"GetTimeSeries processed: df head=\t {df.head()}")
    # logger.debug(f"GetTimeSeries processed: df info: {df.info()}")

    return df


def GetSensorIdsOfType(sensor_type: str) -> pd.DataFrame:
    """ Returns a list of all sensor_id's of the specified type. """

    sql = f"""
    SELECT sensor_id
    FROM tblSensor
    WHERE sensor_type_id IN (SELECT sensor_type_id
                             FROM tblSensorType
                             WHERE type_name = '{sensor_type}');
    """
    df = query(sql)

    return df


def GetSensorTypes() -> pd.DataFrame:
    """ Returns a list of all sensor types. """

    sql = f"""
    SELECT *
    FROM tblSensorType;
    """
    df = query(sql)

    return df


def GetDevices(room_id: str) -> pd.DataFrame:
    """ Returns a list of all devices in the specified room. """

    sql = f"""
    SELECT *
    FROM tblDevice
    WHERE room_id = {room_id};
    """
    df = query(sql)

    return df


# executed when run as script (aka as unit test)
if __name__ == "__main__":
    logger.info("executing DB_tools.py as script...");
    tic = pendulum.now();

    # get list of rooms
    types = GetSensorTypes()
    print(types['type_name'].head)

    ids = GetSensorIdsOfType('temperature')
    print(ids.head)
    # # get sensor id
    # sensorId = GetSensorId("clt-lab-t-6020.zhaw.ch_temperature")
    # print(f"sensor_id= {sensorId}")
    print(ids[:1])
    ts = GetTimeSeries(7)
    print(ts.head)
    #
    # # get time series
    # ts = GetTimeSeries(sensorId, limit=100)
    # print(ts.head)

    toc = pendulum.now() - tic
    print(f"Wall time: {toc.minutes:02}:{toc.seconds:02}+{toc.microseconds / 1000:03}")


