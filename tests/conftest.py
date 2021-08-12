import os
import tempfile
from pathlib import Path
import json

import pytest
from pymongo import MongoClient
from pymongo import errors as mongo_errors
from xonsh.lib import subprocess
from xonsh.lib.os import rmtree


# def pytest_configure():
#     pytest.OUTPUT_FAKE_DB = False
#     pytest.MONGODB_DATABASE_NAME = "test"
#     pytest.CIF_DIR = os.path.join(os.pardir, 'docs\\examples\\cifs')
#     pytest.CIFJSON_COLLECTION_NAME = "cif_json"

OUTPUT_FAKE_DB = False  # always turn it to false after you used it
MONGODB_DATABASE_NAME = "test"
CIF_DIR = os.path.join(os.pardir, 'docs\\examples\\cifs')
CIFJSON_COLLECTION_NAME = "cif_json"


# @pytest.fixture(scope="module")
# def mongo_cif_source_filepath():
#     yield CIF_DIR


@pytest.fixture(scope="module")
def cif_mongodb_client_populated():
    yield from cif_mongodb_client(True)


@pytest.fixture(scope="module")
def cif_mongodb_client_unpopulated():
    yield from cif_mongodb_client(False)


def cif_mongodb_client(populated: bool = False) -> MongoClient:
    """A test fixture that creates and destroys a git repo in a temporary
    directory, as well as a mongo database.
    This will yield a the mongo client with a database named test and collection within named cif_json.
    The collection will contain the test_cif_full from the inputs folder
    """
    forked = False
    name = "regolith_mongo_fake"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    os.mkdir(repo)
    os.chdir(repo)
    mongodbpath = os.path.join(repo, 'dbs')
    os.mkdir(mongodbpath)
    if os.name == 'nt':
        # If on windows, the mongod command cannot be run with the fork or syslog options. Instead, it is installed as
        # a service and the exceptions that would typically be log outputs are handled by the exception handlers below.
        # In addition, the database must always be manually deleted from the windows mongo instance before running a
        # fresh test.
        cmd = ["mongo", MONGODB_DATABASE_NAME, "--eval", "db.dropDatabase()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except subprocess.CalledProcessError:
            print(
                "Mongodb likely has not been installed as a service. In order to run mongodb tests, make sure\n"
                "to install the mongodb community edition with the following link: \n"
                "https://docs.mongodb.com/manual/installation/")
            yield False
            return
        cmd = ["mongostat", "--host", "localhost", "-n", "1"]
    else:
        cmd = ['mongod', '--fork', '--syslog', '--dbpath', mongodbpath]
        forked = True
    try:
        subprocess.check_call(cmd, cwd=repo)
    except subprocess.CalledProcessError:
        print("If using linux or mac, Mongod command failed to execute. If using windows, the status of mongo could \n"
              "not be retrieved. In order to run mongodb tests, make sure to install the mongodb community edition with"
              "\nthe following link:\n"
              "https://docs.mongodb.com/manual/installation/")
        yield False
        return
    try:
        if populated:
            client = example_cifs_to_mongo(MONGODB_DATABASE_NAME)
        else:
            client = True
    except:
        yield False
        return
    yield client
    cmd = ["mongo", MONGODB_DATABASE_NAME, "--eval", "db.dropDatabase()"]
    try:
        subprocess.check_call(cmd, cwd=repo)
    except subprocess.CalledProcessError:
        print(f'Deleting the test database failed, insert \"mongo {MONGODB_DATABASE_NAME} --eval '
              f'\"db.dropDatabase()\"\" into command line manually')
    shut_down_fork(forked, repo)
    if not OUTPUT_FAKE_DB:
        rmtree(repo)


def shut_down_fork(forked, repo):
    if forked:
        cmd = ["mongo", "admin", "--eval", "db.shutdownServer()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except subprocess.CalledProcessError:
            print(f'Deleting the test database failed, insert \"mongo admin --eval '
                  f'\"db.shutdownServer()\"\" into command line manually')


def example_cifs_to_mongo(mongo_db_name):
    from pydatarecognition.cif_io import cif_read
    client = MongoClient('localhost', serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client[mongo_db_name]
    col = db[CIFJSON_COLLECTION_NAME]
    ciffiles = Path(CIF_DIR).glob("*.cif")
    for ciffile in ciffiles:
        print(ciffile.name)
        ciffile_path = Path(ciffile)
        pcd = cif_read(ciffile_path)
        dict = json.loads(pcd.json(by_alias=True))
        try:
            col.insert_one(dict)
        except mongo_errors.DuplicateKeyError:
            print('Duplicate key error, check exemplars for duplicates if tests fail')
        except mongo_errors.BulkWriteError:
            print('Duplicate key error, check exemplars for duplicates if tests fail')
        except Exception as e:
            print(e)
    return client
