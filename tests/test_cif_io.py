from pathlib import Path

import numpy
import pytest
from testfixtures import TempDirectory
from pydatarecognition.cif_io import cif_read, user_input_read, _xy_write, rank_write, set_client
from pydatarecognition.powdercif import PowderCif
from tests.inputs.test_cifs import testciffiles_contents_expecteds
from habanero import Crossref

@pytest.mark.parametrize("cm", testciffiles_contents_expecteds)
def test_cif_read(cm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        cif_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_cif.cif",
                cif_bitstream)
        test_cif_path = temp_dir / f"test_cif.cif"
        actual = cif_read(test_cif_path)
    # build a PowderCif object with the right stuff in it for comparing with that
    #    built by the cif reader
    expected = PowderCif(
        cm[1].get("iucrid"), "deg", cm[1].get("ttheta"),
        cm[1].get("intensity"), wavelength=cm[1].get("wavelength"),
        wavel_units="nm"
    )
    assert actual.iucrid == expected.iucrid
    if cm[1].get('wavelength'):
        assert numpy.allclose(actual.q, expected.q)
    assert numpy.allclose(actual.ttheta, expected.ttheta)
    assert numpy.allclose(actual.intensity, expected.intensity)
    assert actual.wavelength == expected.wavelength

    with TempDirectory() as d:
        temp_dir = Path(d.path)
        cif_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_cif.cif",
                cif_bitstream)
        test_cif_path = temp_dir / f"test_cif.cif"
        actual = cif_read(test_cif_path, verbose = True)
    assert actual.iucrid == expected.iucrid
    if cm[1].get('wavelength'):
        assert numpy.allclose(actual.q, expected.q)
    assert numpy.allclose(actual.ttheta, expected.ttheta)
    assert numpy.allclose(actual.intensity, expected.intensity)
    assert actual.wavelength == expected.wavelength

    if actual.wavelength:
        # This second test is meant to test that the cache was created and now utilized
        with TempDirectory() as d:
            temp_dir = Path(d.path)
            cif_bitstream = bytearray(cm[0], 'utf8')
            d.write(f"test_cif.cif",
                    cif_bitstream)
            test_cif_path = temp_dir / f"test_cif.cif"
            cif_read(test_cif_path)
            actual = cif_read(test_cif_path)
        # build a PowderCif object with the right stuff in it for comparing with that
        #    built by the cif reader
            expected = PowderCif(
                cm[1].get("iucrid"), "invnm", cm[1].get("q"),
                cm[1].get("intensity"), wavelength=None
            )
        assert actual.iucrid == expected.iucrid
        assert numpy.allclose(actual.q, expected.q)
        assert numpy.allclose(actual.intensity, expected.intensity)
        # wavel_units will only be None if the data is retrieved from the cache
        assert actual.wavel_units is None


testuserdata_contents_expecteds = [
    ("\
10.0413\t2037.0\n\
10.0913\t2212.0\n\
10.1413\t2155.0\n\
",
     numpy.array([[10.0413, 10.0913, 10.1413],
                  [2037.0, 2212.0, 2155.0]
                  ])
     ),
    ("\
10.0413\t2037.0\t55\n\
10.0913\t2212.0\t56\n\
10.1413\t2155.0\t57\n\
",
     numpy.array([[10.0413, 10.0913, 10.1413],
                  [2037.0, 2212.0, 2155.0],
                  [55, 56, 57]
                  ])
     )
]

@pytest.mark.parametrize("cm", testuserdata_contents_expecteds)
def test_user_input_read(cm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        userdata_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_userdata.txt",
                userdata_bitstream)
        test_userdata_path = temp_dir / f"test_userdata.txt"
        actual = user_input_read(test_userdata_path)
    expected = cm[1]
    numpy.testing.assert_array_equal(actual, expected)

pm = [
    (([1.0, 2, 3.2],
      [4, 5.5, 6]),
       '1.000000000000000000e+00\t4.000000000000000000e+00\n' \
       '2.000000000000000000e+00\t5.500000000000000000e+00\n' \
       '3.200000000000000178e+00\t6.000000000000000000e+00\n'),
]
@pytest.mark.parametrize("pm", pm)
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


tab_char = '\t'

expected_reference = "Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971)."

rw = [
    (([{'score': 0.99900, 'doi': '10.1107/S0108768102003476', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       {'score': 0.999000, 'doi': '10.1107/S0108768102003476', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       {'score': 0.70610, 'doi': '10.1107/S0108768102003476', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       {'score': 0.70610, 'doi': '10.1107/S0108768102003476', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       {'score': 0.70540, 'doi': '10.1107/S0108768101016330', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       {'score': 0.70540, 'doi': '10.1107/S0108768101016330', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       {'score': 0.65500, 'doi': '10.1107/S0108768101016330', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       {'score': 0.65500, 'doi': '10.1107/S0108270102019637', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       {'score': 0.32100, 'doi': '10.1107/S010876810402693X', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       {'score': 0.32100, 'doi': '10.1107/S0108768105025991', 'ref' : 'Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).'},
       ]),
        f'Rank\tScore\tDOI\t\t\t\t\t\t\tReference\n'
        f'1\t\t0.9990\t10.1107/S0108768102003476\t{expected_reference}\n'
        f'2\t\t0.9990\t10.1107/S0108768102003476\t{expected_reference}\n'
        f'3\t\t0.7061\t10.1107/S0108768102003476\t{expected_reference}\n'
        f'4\t\t0.7061\t10.1107/S0108768102003476\t{expected_reference}\n'
        f'5\t\t0.7054\t10.1107/S0108768101016330\t{expected_reference}\n'
        f'6\t\t0.7054\t10.1107/S0108768101016330\t{expected_reference}\n'
        f'7\t\t0.6550\t10.1107/S0108768101016330\t{expected_reference}\n'
        f'8\t\t0.6550\t10.1107/S0108270102019637\t{expected_reference}\n'
        f'9\t\t0.3210\t10.1107/S010876810402693X\t{expected_reference}\n'
        f'10\t\t0.3210\t10.1107/S0108768105025991\t{expected_reference}\n'
     ),
]
@pytest.mark.parametrize("rw", rw)
def test_rank_write(rw, monkeypatch):
    def mockreturn(*args, **kwargs):
        mock_article = {'message': {'author': [{"given": "SJL", "family": "Billinge"}],
                                    "short-container-title": ["J. Great Results"],
                                    "volume": 10,
                                    "title": ["Whamo"],
                                    "page": "231-233",
                                    "issued": {"date-parts": [[1971,8,20]]}}
                        }
        return mock_article

    monkeypatch.setattr(Crossref, "works", mockreturn)
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        output_file_path = temp_dir
        cif_ranks = rw[0]
        rank_write(cif_ranks, output_file_path, "cifs")
        assert output_file_path.exists()
        expected = rw[1]
        with open(Path(output_file_path) / 'rank_PyCharm_Notepad++_cifs.txt') as f:
            actual = f.read()
        assert actual == expected
        # assert True


mpcontribs_tst = [
    ('mpc', 'This function is not yet implemented'),
    ('fs', None),
    (False, 'mpc_client must be either mpc or fs')
]


@pytest.mark.parametrize("inpt, expected", mpcontribs_tst)
def test_set_client(inpt, expected):
    result = set_client(inpt)

    # TODO: Implement test cases for unexpected input
    # if inpt != 'mpc' and inpt != 'fs':
    #     assert result == expected
    assert result == expected

# End of file.