from collections import defaultdict
from pathlib import Path
from testfixtures import TempDirectory

import pytest
import os

from pydatarecognition.fsclient import FileSystemClient
from pydatarecognition.runcontrol import connect_db
from tests.inputs.pydr_rc import pydr_rc
from tests.inputs.exemplars import EXEMPLARS

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


test_insert_json = [({'intensity': [], 'q': [], 'ttheta': [], 'wavelength': 0.111111, '_id': 'ts1129'},
                   {'intensity': [], 'q': [], 'ttheta': [], 'wavelength': 0.111111, '_id': 'ts1129'})]
@pytest.mark.parametrize('input, result', test_insert_json)
def test_insert_one(rc, input, result):
    client = FileSystemClient(rc)
    client.open()

    dbname = 'local'
    collname = 'calculated'

    client.load_database(pydr_rc['databases'][0])

    client.insert_one(dbname, collname, input)

    assert client.find_one(dbname, collname, {'_id': 'ts1129'}) == result


test_insert_json_bad = [{'bad_case_test_dict': 'bad'}, 'bad_case_test_str']
def test_insert_one_bad(rc):
    client = FileSystemClient(rc)
    client.open()

    dbname = 'local'
    collname = 'calculated'

    client.load_database(pydr_rc['databases'][0])

    with pytest.raises(KeyError, match=r"Bad value in database entry key bad_entry_key"):
        client.insert_one(dbname, collname, test_insert_json_bad[0])

    with pytest.raises(TypeError, match=r"Wrong document format bad_doc_format"):
        client.insert_one(dbname, collname, test_insert_json_bad[1])


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
