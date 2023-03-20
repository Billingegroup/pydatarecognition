from collections import defaultdict
from pathlib import Path
from testfixtures import TempDirectory

import pytest
import tempfile

from pydatarecognition.fsclient import FileSystemClient
from pydatarecognition.cif_io import cif_read, powdercif_to_json, json_dump
from pydatarecognition.runcontrol import DEFAULT_RC, load_rcfile
from tests.inputs.test_calculated_cifs_input import calculated_cifs
from tests.inputs.pydr_rc import pydr_rc


# def test_dump_json():
#     doc = {'first': {'_id': 'first', 'name': 'me', 'date': datetime.date(2021,5,1),
#            'test_list': [5, 4]},
#            'second': {'_id': 'second'}
#            }
#     json_doc = ('{'_id': 'first', 'date': '2021-05-01', 'name': 'me', 'test_list': [5, 4]}\n{'_id': 'second'}')
#     temp_dir = Path(tempfile.gettempdir())
#     filename = temp_dir / 'test.json'
#     dump_json(filename, doc, date_handler=date_encoder)
#     with open(filename, 'r', encoding='utf-8') as f:
#         actual = f.read()
#     assert actual == json_doc


rc = DEFAULT_RC
with TempDirectory() as d:
    temp_dir = Path(d.path)
    d.write(f"pydr_rc.json",
            pydr_rc)
    rc._update(load_rcfile(temp_dir / "pydr_rc.json"))


# FileSystemClient methods tested here
def test_is_alive():
    expected = True  # filesystem is always alive!
    fsc = FileSystemClient(rc)
    actual = fsc.is_alive()

    assert actual == expected


def test_open():
    fsc = FileSystemClient(rc)
    fsc.open()

    # assert fsc.dbs == rc.databases
    assert isinstance(fsc.dbs, type(defaultdict(lambda: defaultdict(dict))))
    assert isinstance(fsc.chained_db, type(dict()))
    assert not fsc.closed


def test_close():
    fsc = FileSystemClient(rc)
    assert fsc.open
    # assert fsc.dbs == rc.databases
    assert isinstance(fsc.dbs, type(defaultdict(lambda: defaultdict(dict))))

    actual = fsc.close()
    assert fsc.dbs is None
    assert fsc.closed


@pytest.mark.skip('Not written')
def test_load_json():
    pass


@pytest.mark.skip('Not written')
def test_load_yaml():
    pass


@pytest.mark.skip('Not written')
def test_load_cif():
    pass


@pytest.mark.skip('Not written')
def test_load_database():
    pass


@pytest.mark.skip('Not written')
def test_dump_json():
    pass


@pytest.mark.skip('Not written')
def test_dump_yaml():
    pass


@pytest.mark.skip('Not written')
def test_dump_cif():
    pass


@pytest.mark.skip('Not written')
def test_dump_database():
    pass


@pytest.mark.skip('Not written')
def test_keys():
    pass


@pytest.mark.skip('Not written')
def test_collection_names():
    pass


@pytest.mark.skip('Not written')
def test_all_documents():
    pass


@pytest.mark.skip('Not written')
def test_insert_one():
    pass


@pytest.mark.skip('Not written')
def test_insert_many():
    pass


@pytest.mark.skip('Not written')
def test_delete_one():
    pass


@pytest.mark.parametrize('cm', calculated_cifs)
def test_find_one(cm):
    client = FileSystemClient(rc)

    with TempDirectory() as d:
        temp_dir = Path(d.path)
        name = 'right'

        for cif in cm:
            cif_bitstream = bytearray(cif, 'utf8')
            d.write(f'{name}.cif', cif_bitstream)
            test_cif_path = temp_dir / f'{name}.cif'
            cif = cif_read(test_cif_path)
            json_dump(powdercif_to_json(cif), temp_dir / f'{name}.json')

            name = 'wrong'

        # Tentative
        expected = d.read(str(temp_dir / 'right.json'), 'utf-8')

        client.dbs['cifs']['calculated'][cif_path1.split('/')[-1][:-18]] = expected
        client.dbs['cifs']['calculated'][cif_path2.split('/')[-1][:-18]] = d.read(str(temp_dir / 'wrong.json'), 'utf-8')

        actual = client.find_one('cifs', 'calculated', {'iucrid': 'bs0018'})

        print(client.dbs['cifs']['calculated'].values())

        assert actual == expected

        # TODO: Runcontrol?


@pytest.mark.skip('Not written')
def test_update_one():
    pass
