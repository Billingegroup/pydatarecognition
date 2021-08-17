from pathlib import Path
import json

from pydatarecognition.cif_io import cif_read
from pymongo import MongoClient


def cifs_to_mongo(mongo_db_uri: str, mongo_db_name: str, mongo_collection_name: str, cif_filepath: str) -> MongoClient:
    """
    Adds all cifs found in the cif_filepath directory to the collection pointed to by the uri, db, and collection name
    @param mongo_db_uri: First arg to MongoClient of pymongo. Can be localhost or atlas server e.g.
    mongodb+srv://<username>:<password>@<clustername>.uc5ro.mongodb.net/<databasename>?retryWrites=true&w=majority
    @param mongo_db_name: Database in mongodb to upload CIF data to
    @param mongo_collection_name: Collection in mongodb to upload CIF data to
    @param cif_filepath: Directory containing CIFs that will be uploaded in it's entirety
    @return: Client at the level specified in the URI (e.g. database level if <databasename> provided)
    """
    client = MongoClient(mongo_db_uri, serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client[mongo_db_name]
    col = db[mongo_collection_name]
    ciffiles = Path(cif_filepath).glob("*.cif")
    for ciffile in ciffiles:
        print(ciffile.name)
        ciffile_path = Path(ciffile)
        pcd = cif_read(ciffile_path)
        dict = json.loads(pcd.json(by_alias=True))
        col.insert_one(dict)
    return client


if __name__ == "__main__":
    import os
    import yaml

    from google.cloud import storage

    filepath = Path(os.path.abspath(__file__))

    if os.path.isfile(os.path.join(filepath.parent.absolute(), '../requirements/testing-cif-datarec-secret.json')):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(filepath.parent.absolute(),
                                                                    '../requirements/testing-cif-datarec-secret.json')
    storage_client = storage.Client()
    storage_client.create_bucket('raw_cif_data')
    CIF_DIR = filepath.parent.parent / 'docs' / 'examples' / 'cifs'
    with open('secret_password.yml', 'r') as f:
        secret_dict = yaml.safe_load(f)
    # URI for group DB f'mongodb+srv://{secret_dict["username"]}:{secret_dict["password"]}@cluster0.9bj1h.mongodb.net/?retryWrites=true&w=majority'
    # URI for zt altas db f'mongodb+srv://{secret_dict["username"]}:{secret_dict["password"]}@sidewinder.uc5ro.mongodb.net/?retryWrites=true&w=majority'
    client = cifs_to_mongo(f'mongodb+srv://{secret_dict["username"]}:{secret_dict["password"]}@sidewinder.uc5ro.mongodb.net/?retryWrites=true&w=majority', "test",
                            "cif", CIF_DIR)
    db = client["test"]
    coll = db["cif"]
    mongo_collections = list(coll.find({}))
    pass
