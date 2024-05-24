import logging
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import kpss
from src import config
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.seasonal import STL
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Category20  # For color palettes
from bokeh.models import ColumnDataSource
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import src.data.DB_tools as dbt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import time
import matplotlib.pyplot as plt


logger = logging.getLogger(__name__)


def download_all_data(start_date : str="2024-01-01"):  # Due to the faulty data before 2024
    """Download all the data from the DB
    Parameters: start_date (default "2024-01-01")
    Returns: DataFrame incl all the sensor data
    """
    logger.info("Downloading all data")
    base_dir = Path.cwd()  # Adjust this if your script is in a different directory structure
    output_dir = base_dir / 'data' / 'raw'
    output_dir.mkdir(parents=True, exist_ok=True)

    sensor_types = dbt.GetSensorTypes()
    sensor_data_dfs = {}  # Dictionary to store dataframes for each sensor type

    for sensor_type in sensor_types['type_name']:
        print(f"Processing {sensor_type} sensors")
        sensor_ids = dbt.GetSensorIdsOfType(sensor_type)

        all_sensor_data = []

        for sensor_id in tqdm(sensor_ids['sensor_id'], desc=f"Downloading {sensor_type} sensor data"):
            sensor_data = dbt.GetTimeSeries(sensor_id, start_date=start_date)
            if sensor_data.empty:
                continue

            sensor_data.set_index('timestamp', inplace=True)
            sensor_data.rename(columns={'value': f'sensor_{sensor_id}'}, inplace=True)
            all_sensor_data.append(sensor_data)

        if all_sensor_data:
            combined_data = pd.concat(all_sensor_data)
            file_path = output_dir / f'{sensor_type}_data.parquet'
            combined_data.to_parquet(file_path)
            sensor_data_dfs[sensor_type] = combined_data
        else:
            sensor_data_dfs[sensor_type] = pd.DataFrame()  # Store an empty DataFrame if no data
    logger.info("Successfully downloaded all data")
    return sensor_data_dfs


def load_sensor_data(directory):
    """Load the sensor data
    Parameters: directory (str)
    Returns: sensor_data (DataFrame)"""
    logger.info("Loading sensor data")
    # Define the directory path for the Parquet files
    data_dir = Path(directory)

    # Create a dictionary to store each DataFrame
    sensor_data_dfs = {}

    # List all Parquet files in the directory
    parquet_files = data_dir.glob('*.parquet')

    # Load each Parquet file into a DataFrame and store it in the dictionary
    for file_path in parquet_files:
        # Assume the file name format is 'sensor_type_data.parquet'
        sensor_type = file_path.stem.replace('_data', '')  # Extract sensor type from file name
        df = pd.read_parquet(file_path)
        sensor_data_dfs[sensor_type] = df

    return sensor_data_dfs


def stationarity_tests(df):
    """
    Performs stationarity tests on a given time series data using the Augmented Dickey-Fuller (ADF) test
    and the Kwiatkowski-Phillips-Schmidt-Shin (KPSS) test. These tests help determine the presence of a unit
    root in the series, which indicates non-stationarity.

    The ADF test checks for stationarity against an alternative hypothesis of a unit root (non-stationarity).
    The KPSS test, on the other hand, tests for stationarity around a deterministic trend (i.e., trend-stationarity)
    against the alternative of stationarity.

    Parameters:
    - df (pd.DataFrame): A pandas DataFrame containing the time series data. The DataFrame should have
      a single column if it contains time series values and be indexed by datetime.

    Logging:
    - The function logs the initiation of the stationarity test and the results of both the ADF and KPSS tests.
    """

    logger.info("Stationarity tests")
    adf = adfuller(df, regression='ct')
    kp = kpss(df, regression='ct')
    # log results
    logger.info(f'p-value of adf:\n {adf[1]}\n \n p-value of the kpss: \n{kp[1]}')
    #return adf, kp # exchange thru logger!
    return

def resample_data(df, downsampling_rate : str =  '2min', upsampling_rate : str = '0.1min'):
    """
    Resample the data first by upsampling to a finer granularity, then interpolating missing values,
    and finally downsampling to a coarser granularity.

    Parameters:
    df (pd.DataFrame): The dataframe to resample.
    downsampling_rate (str): The rate for downsampling, default is '2min'.
    upsampling_rate (str): The rate for upsampling, default is '0.1min'.

    Returns:
    pd.DataFrame: The resampled dataframe.
    """
    logger.info("Resampling data")
    try:
        upsampled = df.resample(upsampling_rate).mean()
        interpolated = upsampled.interpolate(method='linear')
        downsampled = interpolated.resample(downsampling_rate).mean()
        logger.info(f'Data has been upsampled to :{upsampling_rate} and downsampled to {downsampling_rate}"')
    except Exception as e:
        logger.debug(e)
    return downsampled

def seasonal_decomposition(df: pd.DataFrame, model_type: str = 'multiplicative', period = 720):
    """
    Decomposes a time series into seasonal, trend, and residual components using specified model type and period.
    This function is useful for analyzing patterns within time series data.

    Args:
    df (pd.DataFrame): Time series data as a DataFrame.
    model_type (str): Type of decomposition model ('additive' or 'multiplicative'). Default is 'multiplicative'.
    period (int): The frequency of the time series. Default is 24 (e.g., hourly data for a full day).

    Effect:
    Logs the start and completion of decomposition and plots the decomposed components.
    """
    logger.info("seasonal_decomposition:")
    # Decompose the data
    decomposition = seasonal_decompose(df, model=model_type, period=period)
    # model additive or multiplicative, here we should use multiplicative, see daily/ seasonal highs in co2_data
    logger.info(f"seasonal_decomposition: done with a  {model_type} model and period {period}")
    # Plot the decomposed components
    decomposition.plot()
    return decomposition

def loess_decomposition(df: pd.DataFrame, seasonal: int = 5, period = 720):

    """
    Performs LOESS (Locally Estimated Scatterplot Smoothing) decomposition to analyze and smooth time series data.
    This function fits a series to local regressions, suitable for data with non-linear patterns.

    Args:
    df (pd.DataFrame): Time series data as a DataFrame.
    seasonal (int): The smoothing parameter for seasonal component. Default is 5.
    period (int): The number of observations that complete one seasonal cycle. Default is 52 (e.g., weekly data over a year).

    Effect:
    Logs the start and completion of LOESS fitting and plots the results.
    """
    logger.info("loess_decomposition:")
    stl = STL(df, seasonal=seasonal, period = period)
    res = stl.fit()
    logger.info(f"loess_decomposition: done with a seasonal: {seasonal}  and period {period}")
    res.plot()
    return res


def plot_all_sensors(df):
    """
    Generates an interactive plot for sensor data from a DataFrame where each column is a sensor.
    Saves the plot as an HTML file named after the first column. Uses the Bokeh library for plotting.

    Args:
    df (DataFrame): Sensor data where each column represents a different sensor.
    output_filename (str): Name of the output HTML file. Defaults to the name of the first sensor column with '_plot.html' suffix.

    Returns:
    Displays the interactive plot.
    """
    file_name = df.columns[0]
    output_filename = f"{file_name}_plot.html"
    output_file(output_filename)  # output_notebook() would display plot within the Jupyter Notebook
    # Prepare the plot
    p = figure(title="All Sensor Data", x_axis_type="datetime",
               x_axis_label='Timestamp', y_axis_label='Sensor Values',
               width=1200, height=400)

    # Colors for lines
    colors = Category20[20]  # Supports up to 10 lines; use other palettes for more lines

    # Plot data from each sensor
    for index, column in enumerate(df.columns):
        # Use cyclic colors if more than 10 sensors
        color = colors[index % len(colors)]
        # Create a column data source for each sensor's data
        source = ColumnDataSource(data={
            'timestamp': df.index,
            'values': df[column]
        })
        p.line(x='timestamp', y='values', source=source, legend_label=column, line_width=2, color=color)

    # Styling for the plot
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    return show(p)


def acf_plotting(residuals):
    """
    Plot the Autocorrelation Function (ACF) and the Partial Autocorrelation Function (PACF) of the given residuals.

    Parameters:
    residuals (pd.Series): The residuals of a time series model. It should be a Pandas Series object.

    This function generates two plots:
    1. ACF plot
    2. PACF plot

    The plots are displayed and saved as a PNG file in the './data/images/' directory with a filename that includes
    the name of the residual series and the current timestamp.

    The function also logs the completion of the plotting and saving process.

    Example usage:
    >>> import pandas as pd
    >>> residuals = pd.Series([...])
    >>> acf_plotting(residuals)
    """
    logger.info("plotting ACF:")

    # Plot the ACF and PACF
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))

    plot_acf(residuals.dropna(), ax=axs[0])
    axs[0].set_title('Autocorrelation Function (ACF)')
    axs[0].set_xlabel('Lag')
    axs[0].set_ylabel('ACF')

    plot_pacf(residuals.dropna(), ax=axs[1])
    axs[1].set_title('Partial Autocorrelation Function (PACF)')
    axs[1].set_xlabel('Lag')
    axs[1].set_ylabel('PACF')

    plt.tight_layout()
    timestamp = round(time.time())
    filename = f'../../data/images/acf_{residuals.name}_{timestamp}.png'
    plt.savefig(filename)
    plt.show()

    logging.info(f'ACF and PACF plots saved as {filename}')