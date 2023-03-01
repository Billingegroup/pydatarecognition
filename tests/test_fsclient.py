import tempfile
from pathlib import Path

import pytest

from collections import defaultdict
from testfixtures import TempDirectory

from pydatarecognition.fsclient import FileSystemClient


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


def test_open():
    fsc = FileSystemClient(rc)
    fsc.open()

    assert isinstance(fsc.dbs, type(defaultdict(lambda: defaultdict(dict))))
    assert isinstance(fsc.chained_db, type(dict()))
    assert not fsc.closed


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


def test_close():
    fsc = FileSystemClient(rc)
    fsc.close()

    assert fsc.dbs is None
    assert fsc.closed


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