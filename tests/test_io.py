from pathlib import Path

import CifFile
import numpy
import pytest
from testfixtures import TempDirectory

# from pydatarecognition.io import cif_read, user_data_read
from pydatarecognition.io import _xy_write
from tests.inputs.test_cifs import testciffiles_contents_expecteds
from tests.inputs.test_user_data import testuserdata_contents_expecteds
from tests.inputs.test__xy_write_data import test__xy_write_data_contents_expecteds


@pytest.mark.parametrize("cm", testciffiles_contents_expecteds)
def test_cif_read(cm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        cif_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_cif.cif",
                cif_bitstream)
        test_cif_path = temp_dir / f"test_cif.cif"
        actual = cif_read(test_cif_path)
    # build a CifFile object with the right stuff in it for comparing with that
    #    built by the cif reader
    expected = CifFile.CifFile()
    expected[cm[1].get('block_name')] = CifFile.CifBlock()
    cb = expected[cm[1].get('block_name')]
    for item in cm[1].get('block_items'):
        cb[item[0]] = item[1]
    for item in cm[1].get('loop_items'):
        cb.AddCifItem(([item['keys']], [item['values']]))
    assert actual[cm[1].get('block_name')].items() == expected[
        cm[1].get('block_name')].items()


@pytest.mark.parametrize("cm", testuserdata_contents_expecteds)
def test_user_input_read(cm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        userdata_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_userdata.txt",
                userdata_bitstream)
        test_userdata_path = temp_dir / f"test_userdata.txt"
        actual = user_data_read(test_userdata_path)
    expected = cm[1]
    assert actual == expected


@pytest.mark.parametrize("pm", test__xy_write_data_contents_expecteds)
def test__xy_write(pm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        output_file_path = temp_dir / 'swallow.txt'
        x_array, y_array = numpy.array(pm[0][0]), numpy.array(pm[0][1])
        _xy_write(output_file_path, x_array, y_array)
        assert output_file_path.exists()
        expected = pm[1]
        with open(output_file_path) as f:
            actual = f.read()
        assert actual == expected
