# pyDataRecognition

![pydatarecognition](https://github.com/billingegroup/pydatarecognition/actions/workflows/main.yml/badge.svg)

## Preprint on arXiv 
For a thorough description of the project, please see the paper by Özer *et al.*: 
https://doi.org/10.48550/arXiv.2204.00434.

## Setup and installation

The following guidelines assume that the user runs a conda distribution, i.e. Anaconda or Miniconda.

### Create/activate conda environment
- Create/activate new conda env by running:
  ```shell
  conda create -n pydatarecognition python=3
  conda activate pydatarecognition
  ```
### Install dependencies
- Navigate to the main **pydatarecognition** directory and run:
  ```shell
  conda install --file requirements/run.txt
  pip install -r requirements/pip_requirements.txt
  ```
### Install package
- Install the package by navigating to the main **pydatarecognition** 
  directory and run:
  ```shell
  python setup.py install
  ```

## Running the program

### Directory structure
Currently, the program should be run from a directory  containing the cif files.
Within `docs/examples`, example cifs are located in the `cifs/measured` and `cifs/calculated` subdirectory,  e.g., in `docs/examples/cifs/measured`.

### Example files
Within `docs/examples/powder_data`, three examples on input data files are available:
- 01_Mg-free-whitlockite_wl=1.540598.txt
- 02_BaTiO3_wl=0.1665.txt
- 03_KNaLi-NbMnO3_perovskite_wl=1.5482.txt

### How to run the program
With your `pydatarecognition` conda env activated, to get information on how to run the program type:  
  ```shell
      pydr --help
  ```
or
  ```shell
    pydatarecognition -h
  ```
The program expects a syntax somewhat similar to:
```shell
  python pydatarecognition.main -i INPUTFILE --xquantity XQUANTITY --xunit XUNIT -w WAVELENGTH
  ```
For a full description, please run the program with the help flag as shown above.

### Running the program for the measured data example files
Navigate to `docs/examples/cifs/measured`.

#### Running the program the first example measured data file
```shell
pydr -i ../../powder_data/01_Mg-free-whitlockite_wl=1.540598.txt --xquantity twotheta --xunit deg -w 1.540598
```
#### Running the program for the second example measured data file
```shell
pydr -i ../../powder_data/02_BaTiO3_wl=0.1665.txt --xquantity twotheta --xunit deg -w 0.1665
```
#### Running the program for the third example measured data file
```shell
pydr -i ../../powder_data/03_KNaLi-NbMnO3_perovskite_wl=1.5482.txt --xquantity twotheta --xunit deg -w 1.5482
```

### Running the program for the calculated cif example files
Navigate to `docs/examples/cifs/calculated` and rerun the commands above.


### Program output
Output files will be available in the `_output` folder created in the current working directory, i.e. 
`docs/examples/_output`.
