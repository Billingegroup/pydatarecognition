# pyDataRecognition

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
Currently, the program should be run from a directory with a subdirectory called `cifs`, containing the cif files.
Within `docs/examples`, example cifs are located in the `cifs` subdirectory, i.e. in `docs/examples/cifs`.

### Example files
Within `docs/examples/powder_data`, three examples on input data files are available:
- 01_Mg-free-whitlockite_wl=1.540598.txt
- 02_BaTiO3_wl=0.1665.txt
- 03_(KNaLi)NbMnO3_perovskite_wl=1.5482.txt

### How to run the program
To get information on how to run the program:  
  ```shell
      python -m pydatarecognition.main --help
  ```
or
  ```shell
    python -m pydatarecognition.main -h
  ```
The program expects a syntax somewhat similar to:
```shell
  python pydatarecognition.main -i INPUTFILE --xquantity XQUANTITY --xunit XUNIT -w WAVELENGTH
  ```
For a full description, please run the program with the help flag as shown above.
### Running the program for the example files
Navigate to `docs/examples` where `cifs` and `powder_data` folders are present.

#### Running the program the first example file
```shell
pydatarecognition -i 01_Mg-free-whitlockite_wl=1.540598.txt --xquantity twotheta --xunit deg -w 1.540598
```
#### Running the program for the second example file
```shell
pydatarecognition -i 02_BaTiO3_wl=0.1665.txt --xquantity twotheta --xunit deg -w 0.1665
```
#### Running the program for the third example file
```shell
pydatarecognition -i 03_(KNaLi)NbMnO3_perovskite_wl=1.5482.txt --xquantity twotheta --xunit deg -w 1.5482
```

### Program output
Output files will be available in the `_output` folder created in the current working directory, i.e. 
`docs/examples/_output`.
