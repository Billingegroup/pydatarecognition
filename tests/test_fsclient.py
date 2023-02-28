import datetime

import tempfile
from pathlib import Path

import pytest

#from pydatarecognition.fsclient import date_encoder, dump_json, FileSystemClient
from pydatarecognition.fsclient import FileSystemClient

# def test_date_encoder():
#     day = datetime.date(2021,1,1)
#     time = datetime.datetime(2021, 5, 18, 6, 28, 21, 504549)
#     assert date_encoder(day) == '2021-01-01'
#     assert date_encoder(time) == '2021-05-18T06:28:21.504549'
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

# todo:
# build a runcontrol object as in regolith.  have it created globally in the
# tests for  reuse in all the tests (look for DEFAULT_RC in regoith tests)
# for now:
# DEFAULT_RC = RunControl(
#     _validators=DEFAULT_VALIDATORS,
#     builddir="_build",
#     mongodbpath=property(lambda self: os.path.join(self.builddir, "_dbpath")),
#     user_config=os.path.expanduser("~/.config/regolith/user.json"),
#     force=False,
#     database=None
# )
DEFAULT_RC = {}
rc = DEFAULT_RC


# FileSystemClient methods tested here
def test_is_alive():
    expected = True  # filesystem is always alive!
    fsc = FileSystemClient(rc)
    actual = fsc.is_alive()
    assert actual == expected


@pytest.mark.skip("Not written")
def test_open():
    pass


@pytest.mark.skip("Not written")
def test_load_json():
    pass


@pytest.mark.skip("Not written")
def test_load_yaml():
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
def test_dump_database():
    pass


@pytest.mark.skip("Not written")
def test_close():
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


@pytest.mark.skip("Not written")
def test_insert_one():
    pass


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