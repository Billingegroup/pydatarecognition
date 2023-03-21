import copy
import json

from testfixtures import TempDirectory
from pathlib import Path

from pydatarecognition.runcontrol import DEFAULT_RC, filter_databases, \
    connect_db
from pydatarecognition.database import connect
from tests.inputs.pydr_rc import pydr_rc


def test_connect_db():
    rc = copy.copy(DEFAULT_RC)
    rc._update(pydr_rc)

    filter_databases(rc)
    with connect(rc) as rc.client:
        expected_dbs = rc.client.dbs
        expected_chdb = rc.client.chained_db
    chained_db, dbs = connect_db(rc)
    assert chained_db == expected_chdb
    assert dbs == expected_dbs
