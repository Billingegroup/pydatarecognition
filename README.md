# pyDataRecognition

[![tests](https://circleci.com/github/Billingegroup/pydatarecognition.svg?style=shield&circle-token=b187a993ea69930d37388bf61dccaf499456a481)](<test>)  

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

=====================================
###Development
- Create/activate new conda env
  ```shell
  conda create -n pydatarecognition python>=3.9
  conda activate pydatarecognition
  ```
- Install dependencies (assuming source)
  ```shell
  conda install --file requirements/run.tx
  pip install -r requirements/pip_requirements.txt
  conda install --file requirements/test.txt
  ```

###Google Cloud Storage Development
The pydantic model now automatically exports all numpy arrays to google cloud when they are json serialized.
This should only affect use on the mongo server, since local running of the application leaves out these arrays
when serializing to the cache.  
  
If you would like to develop for the mongo database, you should set up your own GCP service account and put the key
in the project's pydatarecognition folder with the name 'testing-cif-datarec-secret'. Instructions on how to do so 
can be found below.
- create a GCP account and in the top right, go to console
- when in the console, go to the three hexagons in the top left, click, and select new project
- go through the steps, and make sure the project is active
- on the LHS, select the triple bar icon for the dropdown, and go to API's and Services, and go to library
- search google cloud storage and google cloud storage json api, click on each of them, and enable them
- on the LHS, select the triple bar icon for the dropdown, and go to API's and Services, and select service account
- create a new service account with an arbitrary name, as a role, go to basic -> owner and select, skip the final step
- go to keys, click add key, select json, create
- rename this json file to 'testing-cif-datarec-secret.json' and place it in pydatarecognition/pydatarecognition
  
###FastAPI Development
- update your dependencies
  ```shell
  conda install --file requirements/run.txt
  pip install -r requirements/pip_requirements.txt
  ```
- Currently, there are three usernames and passwords required in order to develop the website. One for oauth (env var),
  mongo atlas (yaml file opened in script), for google cloud storage (json file pointed at by ENV var). The latter can
  be ascertained as described above. The former two have been described below.
- Add a secret username and password to a yml file in the pydatarecognition folder named secret_password.yml
  - These should take the following form (you replace the <>, removing the <>)
  ```yaml
  username: <username>
  password: <password>
  ```
- Add an oauth login page to your google cloud platform account () and add the following variables to a .env file in the 
  pydatarecognition directory
  ```shell
  GOOGLE_CLIENT_ID=<client_id_for_oauth>
  GOOGLE_CLIENT_SECRET=<client_secret_for_oauth>
  ```
- run the following command from the base dir terminal to run the app
  ```shell
  uvicorn pydatarecognition.app:app --reload
  ```
- go to the following in your browser to see (and try out) the API
  ```shell
  http://127.0.0.1:8000/docs
  ```
- the \_\_name__=="\_\_main__" section of mongo_utils.py is currently set up to export example cif data to group mongodb
  atlas instance, which is different from the URI currently hardcoded into the fastapi app
  - Be wary of this and feel free to develop in your own free mongo atlas instance (or locally with no need for username
    or password)
- start to make the app look more like the following project https://github.com/markqiu/fastapi-mongodb-realworld-example-app
