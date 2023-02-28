import datetime

import tempfile
from pathlib import Path

import pytest

#from pydatarecognition.fsclient import date_encoder, dump_json, FileSystemClient
from pydatarecognition.mpcclient import MPCClient


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


# MPCClients methods tested here
@pytest.mark.skip("Not written")
def test_is_alive():
    pass


@pytest.mark.skip("Not written")
def test_open():
    pass


@pytest.mark.skip("Not written")
def test_load_database():
    pass


@pytest.mark.skip("Not written")
def test_import_database():
    pass


@pytest.mark.skip("Not written")
def test_export_database():
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
