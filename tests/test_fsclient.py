import numpy as np
import pytest
import os

from pathlib import Path
from collections import defaultdict
from glob import iglob

from pydatarecognition.cif_io import cif_read
from pydatarecognition.fsclient import FileSystemClient
from tests.cifpath import cif_path


def test_load_cifs():
    cifpath = cif_path
    client = FileSystemClient(None)

    result = client.load_cifs(cifpath)
    expected = defaultdict(lambda: None)

    for f in [file for file in iglob(os.path.join(cifpath, "*.cif"))]:
        ciffilename = os.path.split(f)[-1]
        expected[ciffilename] = cif_read(Path(f))

    for key in expected:
        assert np.all([expected[key], client[key]])
