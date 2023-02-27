import numpy
import pytest
import os

from pathlib import Path
from collections import defaultdict
from glob import iglob

from pydatarecognition.fsclient import FileSystemClient
from pydatarecognition.cif_io import cif_read
from cifpath import cif_path


def test_load_cifs():
    cifpath = cif_path
    client = FileSystemClient(None)

    result = client.load_cifs(cifpath)
    expected = defaultdict(lambda: None)

    for f in [file for file in iglob(os.path.join(cifpath, "*.cif"))]:
        ciffilename = os.path.split(f)[-1]
        expected[ciffilename] = cif_read(Path(f))

    assert result == expected
