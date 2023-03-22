import copy
import json

from testfixtures import TempDirectory
from pathlib import Path

from pydatarecognition.runcontrol import filter_databases, connect_db
from pydatarecognition.database import connect


def test_connect_db(rc):
    filter_databases(rc)
    with connect(rc) as rc.client:
        expected_dbs = rc.client.dbs
        expected_chdb = rc.client.chained_db
    dbs = connect_db(rc)
    # assert chained_db == expected_chdb
    assert dbs == expected_dbs
