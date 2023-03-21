import os
import tempfile
from pathlib import Path
import json

import pytest
from pymongo import MongoClient
from pymongo import errors as mongo_errors
from xonsh.lib import subprocess
from xonsh.lib.os import rmtree
from pydatarecognition.powdercif import storage, BUCKET_NAME
from pydatarecognition.fsclient import dump_yaml
from tests.inputs.exemplars import EXEMPLARS
from google.cloud.exceptions import Conflict
from copy import deepcopy


OUTPUT_FAKE_DB = True  # always turn it to false after you used it
MONGODB_DATABASE_NAME = "test"
FS_DATABASE_NAME = "test"
CIF_DIR = os.path.join(os.pardir, 'docs/examples/cifs/calculated')
CIFJSON_COLLECTION_NAME = "cif_json"


@pytest.fixture(scope="function")
def cif_mongodb_client_populated():
    yield from cif_mongodb_client(True)


@pytest.fixture(scope="function")
def cif_mongodb_client_unpopulated():
    yield from cif_mongodb_client(False)


@pytest.fixture(scope="session")
def make_db():
    """A test fixture that creates and destroys a git repo in a temporary
    directory.
    This will yield the path to the repo.
    """
    cwd = os.getcwd()
    name = "pydr_fake"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    os.mkdir(repo)
    os.chdir(repo)
    with open("pydr_rc.json", "w") as f:
        json.dump(
            {
                "default_user_id": "sbillinge",
                "groupname": "billinge-group",
                "databases": [
                    {
                        "name": "test",
                        "url": repo,
                        "public": True,
                        "path": "db",
                        "local": True,
                        "backend": "filesystem"
                    }
                ]
            },
            f
        )
    fspath = os.path.join(repo, 'db')
    os.mkdir(fspath)
    example_cifs_to_fs(fspath)
    yield repo
    os.chdir(cwd)
    if not OUTPUT_FAKE_DB:
        rmtree(repo)


@pytest.fixture(scope="session")
def make_bad_db():
    """A test fixture that creates and destroys a git repo in a temporary
    directory.
    This will yield the path to the repo.
    """
    cwd = os.getcwd()
    name = "pydr_fake_bad"
    repo = os.path.join(tempfile.gettempdir(), name)
    if os.path.exists(repo):
        rmtree(repo)
    os.mkdir(repo)
    os.chdir(repo)
    with open("pydr_rc.json", "w") as f:
        json.dump(
            {
                "default_user_id": "sbillinge",
                "groupname": "billinge-group",
                "databases": [
                    {
                        "name": "test",
                        "url": repo,
                        "public": True,
                        "path": "db",
                        "local": True,
                        "backend": "filesystem"
                    }
                ]
            },
            f
        )
    os.mkdir('db')
    # Write collection docs
    for coll, example in deepcopy(EXEMPLARS).items():
        if isinstance(example, list):
            d = {dd["_id"]: dd for dd in example}
        else:
            d = {example["_id"]: example}
        d.update({"bad": {"_id": "bad", "bad": True}})
        if coll == "measured":
            d.update(
                {
                    "bad_inst": {
                        "_id": "bad_inst",
                        "wavelength": "nowavelength",
                        "ttheta": "nottheta",
                        "q": "noq",
                        "intensity": "nointensity"
                    }
                }
            )
        dump_yaml("db/{}.yaml".format(coll), d)
    yield repo
    os.chdir(cwd)
    if not OUTPUT_FAKE_DB:
        rmtree(repo)


def cif_mongodb_client(populated: bool = False) -> MongoClient:
    """A test fixture that creates and destroys a git repo in a temporary
    directory, as well as a mongo database.
    This will yield a mongo client with a database named test and collection within named cif_json.
    The collection will contain the test_cif_full from the inputs folder
    """
    try:
        storage_client = storage.Client()
    except:
        print("Failed to connect to test storage bucket")
        yield False
        return
    try:
        storage_client.create_bucket(BUCKET_NAME)
    except Conflict:
        pass
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
        storage_client = storage.Client()
        cif_bucket = storage_client.get_bucket(BUCKET_NAME)
        cif_bucket.delete(force=True)


def shut_down_fork(forked, repo):
    if forked:
        cmd = ["mongo", "admin", "--eval", "db.shutdownServer()"]
        try:
            subprocess.check_call(cmd, cwd=repo)
        except subprocess.CalledProcessError:
            print(f'Deleting the test database failed, insert \"mongo admin --eval '
                  f'\"db.shutdownServer()\"\" into command line manually')


def example_cifs_to_fs(fspath, collection_list=None):
    exemplars_copy = deepcopy(EXEMPLARS)
    if collection_list is None:
        exemplars = exemplars_copy
    else:
        exemplars = {k: exemplars_copy[k] for k in collection_list if k in exemplars_copy}
    cwd = os.getcwd()
    os.chdir(fspath)
    for coll, example in exemplars.items():
        if isinstance(example, list):
            d = {dd["_id"]: dd for dd in example}
        else:
            d = {example["_id"]: example}
        dump_yaml("{}.yaml".format(coll), d)
    os.chdir(cwd)


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
