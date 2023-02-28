import numpy as np
import pytest
import os

from pathlib import Path
from testfixtures import TempDirectory

from pydatarecognition.cif_io import cif_read
from pydatarecognition.fsclient import FileSystemClient
from tests.inputs.test_cifs import testciffiles_contents_expecteds


@pytest.mark.parametrize("cm", testciffiles_contents_expecteds)
def test_load_cifs(cm):
    client = FileSystemClient(None)

    with TempDirectory() as d:
        temp_dir = Path(d.path)
        cif_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_cif.cif",
                cif_bitstream)
        test_cif_path = temp_dir / f"test_cif.cif"
        actual = client.load_cifs(temp_dir)['test_cif.cif']
        expected = cif_read(test_cif_path)

        assert actual.iucrid == expected.iucrid
        if cm[1].get('wavelength'):
            if actual.q.shape[0] and expected.q.shape[0]:
                assert np.allclose(actual.q, expected.q)
            if actual.ttheta.shape[0] and len(expected.ttheta):
                assert np.allclose(actual.ttheta, expected.ttheta)

            assert np.allclose(actual.intensity, expected.intensity)
            assert actual.wavelength == expected.wavelength

