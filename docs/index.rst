.. role:: bash(code)
   :language: bash
.. role:: python(code)
   :language: python
.. role::  raw-html(raw)
    :format: html
.. raw:: html

    <link href="_static/unicodetiles.css" rel="stylesheet" type="text/css" />
    <script src="_static/unicodetiles.min.js"></script>
    <script src="_static/rg-dungeon.js"></script>
    <div style="text-align:center;">
        <div id="game"><h1>pyDataRecognition documentation</h1></div>
    </div>
    <script type="text/javascript">initRgDungeon();</script>

What is pyDataRecognition?
====
pyDataRecognition is a structure data content management system for published scientific papers.
pyDataRecognition stores data and metadata relevant for describing the
science in scientific publications and allows it to serialized into structured
databases which may then be mined for better scientific understanding.

pyDataRecognition is developed in the `Billinge group <https://billingegroup.github.io/>`_.

Preprint on arXiv
====
For a thorough description of the project, please see the paper by :raw-html:`&#214;`\zer and Karlsen *et al.*:
https://doi.org/10.48550/arXiv.2204.00434.

Setup and installation
====
The following guidelines assume that the user runs a conda distribution, i.e. Anaconda or Miniconda.

Create/activate conda environment
----
- Create/activate new conda env by running:

.. code-block:: sh

    $ conda create -n pydatarecognition python=3
    $ conda activate pydatarecognition

Install dependencies
----
The pyDataRecognition code is migrating quickly these days.  You can install from the GitHub repository and get the
latest changes. Clone the `GitHub repository  <https://github.com/billingegroup/pydatarecognition>`_, change directory
to the top level directory in that cloned repository where the :bash:`setup.py` file is.

- From inside your conda environment, type

.. code-block:: sh

    $ conda install --file requirements/run.txt
    $ pip install -r requirements/pip_requirements.txt

which installs **pyDataRecognition**, and all its dependencies, in the conda environment. The version of
**pyDataRecognition** you run will change each time you update from the repo leading to instability so be careful.

Install package
----
- Install the package by navigating to the main **pydatarecognition**
  directory and run:

.. code-block:: sh

    $ python setup.py install

Running the program
====

Directory structure
----
Currently, the program should be run from a directory with a subdirectory called :bash:`cifs`, containing the cif files.
Within :bash:`docs/examples`, example cifs are located in the :bash:`cifs` subdirectory, i.e. in
:bash:`docs/examples/cifs`.

Example files
----
Within :bash:`docs/examples/powder_data`, three examples on input data files are available:

- 01_Mg-free-whitlockite_wl=1.540598.txt
- 02_BaTiO3_wl=0.1665.txt
- 03_(KNaLi)NbMnO3_perovskite_wl=1.5482.txt

How to run the program
----
To get information on how to run the program:

.. code-block:: sh

    $ python -m pydatarecognition.main --help

or

.. code-block:: sh

    $ python -m pydatarecognition.main -h

The program expects a syntax somewhat similar to:

.. code-block:: sh

    $ python pydatarecognition.main -i INPUTFILE --xquantity XQUANTITY --xunit XUNIT -w WAVELENGTH

For a full description, please run the program with the help flag as shown above.

Running the program for the example files
----
Navigate to :bash:`docs/examples` where :bash:`cifs` and :bash:`powder_data` folders are present.

Running the program the first example file
^^^^

.. code-block:: sh

    $ python -m pydatarecognition.main -i 01_Mg-free-whitlockite_wl=1.540598.txt --xquantity twotheta --xunit deg -w 1.540598

Running the program for the second example file
^^^^

.. code-block:: sh

    $ python -m pydatarecognition.main -i 02_BaTiO3_wl=0.1665.txt --xquantity twotheta --xunit deg -w 0.1665

Running the program for the third example file
^^^^

.. code-block:: sh

    $ python -m pydatarecognition.main -i 03_(KNaLi)NbMnO3_perovskite_wl=1.5482.txt --xquantity twotheta --xunit deg -w 1.5482

Program output
----
Output files will be available in the :bash:`_output` folder created in the current working directory, i.e.
:bash:`docs/examples/_output`.
