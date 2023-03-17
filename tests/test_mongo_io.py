from pathlib import Path

import numpy as np
import pytest
from pydatarecognition.cif_io import cif_read
from pydatarecognition.powdercif import PydanticPowderCif
from pydatarecognition.mongo_utils import cifs_to_mongo
from tests.conftest import MONGODB_DATABASE_NAME, CIF_DIR, CIFJSON_COLLECTION_NAME

@pytest.mark.skip()
def test_cifs_to_mongo(cif_mongodb_client_unpopulated):
    # this test takes priority. Second test arguably unnecessary but proves existence of conftest infrastructure
    if cif_mongodb_client_unpopulated:
        # ignore the unpopulated database client, as cifs_to_mongo provides its own
        client = cifs_to_mongo('localhost', MONGODB_DATABASE_NAME, CIFJSON_COLLECTION_NAME, CIF_DIR)
        db = client[MONGODB_DATABASE_NAME]
        coll = db[CIFJSON_COLLECTION_NAME]
        mongo_collections = list(coll.find({}))
        mongo_collections = [PydanticPowderCif(**doc) for doc in mongo_collections]
        ciffiles = Path(CIF_DIR).glob("*.cif")
        file_collections = []
        for ciffile in ciffiles:
            print(ciffile.name)
            ciffile_path = Path(ciffile)
            pcd = cif_read(ciffile_path)
            file_collections.append(pcd)
        for mongo_doc in mongo_collections:
            file_doc = [filedoc for filedoc in file_collections if mongo_doc.id == filedoc.id][0]
            for key, value in mongo_doc:
                if key in file_doc.dict().keys():
                    if key == 'ttheta':
                        # ttheta is not cached, and therefore will mismatch on runs that involve caching, as the cache is created alongside mongodb
                        continue
                    if key == 'q' or key == 'intensity':
                        np.allclose(file_doc.dict().get(key), value)
                        continue
                    assert file_doc.dict().get(key) == value
    else:
        pytest.skip('Could not initialize DB')

@pytest.mark.skip()
def test_pydantic_export_import(cif_mongodb_client_populated):
    if cif_mongodb_client_populated:
        db = cif_mongodb_client_populated['test']
        coll = db['cif_json']
        mongo_collections = list(coll.find({}))
        mongo_collections = [PydanticPowderCif(**doc) for doc in mongo_collections]
        ciffiles = Path(CIF_DIR).glob("*.cif")
        file_collections = []
        for ciffile in ciffiles:
            print(ciffile.name)
            ciffile_path = Path(ciffile)
            pcd = cif_read(ciffile_path)
            file_collections.append(pcd)
        for mongo_doc in mongo_collections:
            file_doc = [filedoc for filedoc in file_collections if mongo_doc.id == filedoc.id][0]
            for key, value in mongo_doc:
                if key == 'ttheta':
                    # ttheta is not cached, and therefore will mismatch on runs that involve caching, as the cache is created alongside mongodb
                    continue
                if key == 'q' or key == 'intensity':
                    np.allclose(file_doc.dict().get(key), value)
                    continue
                assert file_doc.dict().get(key) == value
    else:
        pytest.skip('Could not initialize DB')
