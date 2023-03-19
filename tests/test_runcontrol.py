import copy
import json

from testfixtures import TempDirectory
from pathlib import Path

from pydatarecognition.runcontrol import DEFAULT_RC, load_rcfile, filter_databases, \
    connect_db
from pydatarecognition.database import connect


pydr_rc = b"""
{
  "groupname": "Billinge Group",
  "databases": [
    {
      "name": "calculated",
      "url": ".",
      "public": false,
      "path": "db",
      "local": true
    }
  ]
}
"""
def test_connect_db():
    rc = copy.copy(DEFAULT_RC)

    with TempDirectory() as d:
        temp_dir = Path(d.path)
        d.write(f"pydr_rc.json",
                pydr_rc)
        rc._update(load_rcfile(temp_dir / "pydr_rc.json"))
        filter_databases(rc)
        with connect(rc) as rc.client:
            expected_dbs = rc.client.dbs
            expected_chdb = rc.client.chained_db
        chained_db, dbs = connect_db(rc)
        assert chained_db == expected_chdb
        assert dbs == expected_dbs
