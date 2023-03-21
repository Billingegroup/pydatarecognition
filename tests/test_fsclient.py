from collections import defaultdict
from pathlib import Path
from testfixtures import TempDirectory

import pytest
import os

from pydatarecognition.fsclient import FileSystemClient
from pydatarecognition.runcontrol import connect_db

#
# def test_dump_json():
#     doc = {"first": {"_id": "first", "name": "me", "date": datetime.date(2021,5,1),
#            "test_list": [5, 4]},
#            "second": {"_id": "second"}
#            }
#     json_doc = ('{"_id": "first", "date": "2021-05-01", "name": "me", "test_list": [5, 4]}\n{"_id": "second"}')
#     temp_dir = Path(tempfile.gettempdir())
#     filename = temp_dir / "test.json"
#     dump_json(filename, doc, date_handler=date_encoder)
#     with open(filename, 'r', encoding="utf-8") as f:
#         actual = f.read()
#     assert actual == json_doc


# FileSystemClient methods tested here
def test_is_alive(rc):
    expected = True  # filesystem is always alive!
    fsc = FileSystemClient(rc)
    actual = fsc.is_alive()

    assert actual == expected


def test_open(rc):
    fsc = FileSystemClient(rc)
    fsc.open()

    actual = fsc.dbs
    expected = connect_db(rc)[1]
    assert actual == expected

    assert isinstance(fsc.dbs, type(defaultdict(lambda: defaultdict(dict))))
    assert isinstance(fsc.chained_db, type(dict()))
    assert not fsc.closed


def test_close(rc):
    fsc = FileSystemClient(rc)
    assert fsc.open

    actual = fsc.dbs
    expected = connect_db(rc)[1]
    assert actual == expected

    assert isinstance(fsc.dbs, type(defaultdict(lambda: defaultdict(dict))))

    fsc.close()
    assert fsc.dbs is None
    assert fsc.closed


@pytest.mark.skip("Not written")
def test_load_json():
    pass


@pytest.mark.skip("Not written")
def test_load_yaml():
    pass


@pytest.mark.skip("Not written")
def test_load_cif():
    pass


@pytest.mark.skip("Not written")
def test_load_database():
    pass


@pytest.mark.skip("Not written")
def test_dump_json():
    pass


@pytest.mark.skip("Not written")
def test_dump_yaml():
    pass


@pytest.mark.skip("Not written")
def test_dump_cif():
    pass


@pytest.mark.skip("Not written")
def test_dump_database():
    pass


@pytest.mark.skip("Not written")
def test_keys():
    pass


@pytest.mark.skip("Not written")
def test_collection_names():
    pass


@pytest.mark.skip("Not written")
def test_all_documents():
    pass


test_insert_cif = [{'intensity': [], 'q': [], 'ttheta': [], 'wavelength': 0.111111, '_id': 'ts1129'},
                   {'intensity': [], 'q': [], 'ttheta': [], 'wavelength': 0.111111, '_id': 'hi'}]
@pytest.mark.parametrize('tc', test_insert_cif)
def test_insert_one(make_db, rc, tc):
    client = FileSystemClient(rc)
    client.open()

    actual = client.dbs
    expected = connect_db(rc)[1]
    assert actual == expected

    dbname = 'local'
    collname = 'calculated'

    client.insert_one(dbname, collname, tc)

    assert list(client.dbs[dbname][collname].values())[0] == tc  # TODO: How to reformat


@pytest.mark.skip("Not written")
def test_insert_many():
    pass


@pytest.mark.skip("Not written")
def test_delete_one():
    pass


@pytest.mark.skip("Not written")
def test_find_one():
    pass


@pytest.mark.skip("Not written")
def test_update_one():
    pass
