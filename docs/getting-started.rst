Getting started
===============

Intended usage of the SmartBuilding package
-------------------------------------------

By running `main.py`, all the analysis should be performed, i. e. the data processing
pipeline will run, from downloading the data, to model building etc. If individual scripts
are run directly, they should have a unit test defined, which makes development and debugging
easier.

All initializations and the definitions of global parameters occurs in `config.py`, which can 
be imported whenever it is needed.

Overview of what the code does
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^	

Module `make_dataset`
.....................
- The downloaded data is stored in `config.data_raw_dir`, where `config.sensor_types` defines, which sensors are downloaded. 
- The data is resampled and stored in `config.data_processed_dir`.

Module `visualize`
...................
- Defines a general method for plotting time series data. 
- Visualizations are shown as Bokeh plots in the browser and also saved in the `reports` folder.

Notebook `01_pern_StartExploring`
.................................
- Inspects the content of the DB.
- Plots the raw and processed data, but uses the methods also used by `main`, so for downloading and processing the data, the notebook is not needed.

Notebook `02_pern_TimeSeriesAnalysis`
.....................................
TODO


Logger
------

- The root logger is configured in `config.py`. To use this configuration, `import config` in the skript and get a named logger with `logger = logging.getLogger(__name__)`.
- The root logger is setup to log to a file and to the console. The console handler is set to INFO level, which is convenient because instead of using `print()` to display information, you can use `logger.info()` and see the output in the console and in the file. The file is helpful for longer outputs.


Imports
-------

The imports work as expected, because the package is installed in edit mode with `pip install -e .` when
the environment is setup.

Update Sphinx documentation
---------------------------

Whenever new modules are added, change to the `docs` directory and run `sphinx-apidoc -o docs src`. 
This adds `.rst` files for each new package and module. Add the newly created `.rst` files to some 
section with a toctree in `docs/index.rst`.

..note:: Sphinx is configured such that it can also show `Markdown (md)` files.

To build the documentation, change to the `docs` directory and run `sphinx-build -b html . _build`. The documentation is
then available in `docs/_build/html/index.html`.

Project Organization
--------------------

The directory structure is based on the `cookiecutter data science project template <https://drivendata.github.io/cookiecutter-data-science/>`_, and
adapted to our needs. Most notably the makefile has been removed and a `main.py` has been added which runs the analysis pipeline.

The directory structure is as follows:

::

    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py


Installation of the template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^	

Originally, the template was installed with:

::

    pip install pipx
    pipx install cookiecutter
    pipx ensurepath
    cookiecutter gh:drivendata/cookiecutter-data-science

To use the `makefile`, install the make utility via `winget install GnuWin32.Make` and add the path
to VSC's settings by searching for `terminal.integrated.env.windows` in the preferences. Add
::

    {
        "terminal.integrated.env.windows": {
            "Path": "C:\\Program Files (x86)\\GnuWin32\\bin;%Path%"
        }
    }
    
to `settings.json`. Unfortunately, other commands, such as `find` are still missing.
The SmartBuilding template, thus, does not use the makefile. Building the environment 
from the `environment.yml` file is done with `conda env create -f environment.yml`, which
is anyways the more convenient way.

