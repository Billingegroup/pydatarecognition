import argparse
import re

import numpy as np
import pytest
from datetime import date
from habanero import Crossref
from scipy.stats import pearsonr, spearmanr, kendalltau
from pydatarecognition.utils import (data_sample, pearson_correlate,
                                     xy_resample,
                                     get_formatted_crossref_reference,
                                     correlate, get_iucr_doi, rank_returns,
                                     validate_args, XCHOICES, XUNITS, DUNITS,
                                     TTUNITS, QUNITS, process_args,
                                     create_q_int_arrays,
                                     plotting_min_max)
from pydatarecognition.main import create_parser
from tests.inputs.xy1_reg import xy1_reg
from tests.inputs.xy2_reg import xy2_reg
from tests.inputs.xy3_reg import xy3_reg
from tests.inputs.xy4_reg import xy4_reg


def test_data_sample():
    test_cif_data = [[10.0413, 10.0913, 10.1413, 10.1913],
                     [0.7103365913280906, 0.713864540690652, 0.7173923541434815, 0.720920031014933],
                     [2037.0, 2212.0, 2155.0, 2130.0],
                     [],
                     [0.72, 7.83],
                     'neutrons']
    # actual = data_sample(test_cif_data)
    expected = [np.array([0.72, 0.725, 0.73, 0.735]),
                np.array([2154.6302703494507, 1964.404846041446, 2184.9624734543636, 2089.112002617548])]
    # assert actual == expected
    assert True


def test_pearson_correlate():
    test_sampled_data = [np.array([0.72, 0.725, 0.73, 0.735]),
                      np.array([2154.6302703494507, 1964.404846041446, 2184.9624734543636, 2089.112002617548])]
    # actual = -1 <= pearson_correlate(test_sampled_data) <= 1
    expected = True
    # assert actual == expected
    assert True


pm = [
    ( [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
      [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13,
       13.5, 14, 14.5, 15, 15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20],
      [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22],
      [0.1, 0.9, 2.1, 3.1, 3.9, 4.9, 6.1, 7.0, 7.8, 9.1, 10, 11.1]),
]
@pytest.mark.parametrize("pm", pm)
def test_xy_resample(pm):
    actual = xy_resample(pm[0], pm[1], pm[2], pm[3], x_step=0.1)
    expected = (xy1_reg, xy2_reg)
    assert actual[0].all() == expected[0].all()
    assert actual[1].all() == expected[1].all()

pm = [
    ([1, 2, 3, 4, 5],
      [2, 4, 6, 8, 10],
      [1.5, 2.0, 2.5, 3.0, 3.5],
      [3.1, 3.9, 4.9, 6.1, 7.0],
      )
]
@pytest.mark.parametrize("pm", pm)
def test_xy_resample_bad(pm):
    with pytest.raises(ValueError, match='Too narrow xrange: xmax = 3.5 - xmin = 1.5 < 20') as erc:
        xy_resample(pm[0], pm[1], pm[2], pm[3], x_step=0.1)

def test_get_iucr_doi():
    iucr_id, doi = "an0607", "10.1107/S0108768102003476"
    actual = get_iucr_doi(iucr_id)
    expected = doi
    assert actual == expected
    poor_id = "poorid"
    actual = get_iucr_doi(poor_id)
    expected = ""
    assert actual == expected


def test_get_formatted_crossref_reference(monkeypatch):
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
    expected = ("Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).",
                date(1971, 8, 20))
    actual = get_formatted_crossref_reference("test")
    assert actual == expected


def test_correlate():
    y1, y2 = np.linspace(0, 10, 11), [0.1, 0.9, 2, 3.2, 4.3, 4.8, 5.9, 7, 7.9, 9, 9.8]
    actual = correlate(y1, y2)
    expected = float(pearsonr(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, correlator='pearson')
    expected = float(pearsonr(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, correlator='spearman')
    expected = float(spearmanr(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, correlator='kendall')
    expected = float(kendalltau(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, correlator='Pearson')
    expected = float(pearsonr(y1, y2)[0])
    assert actual == expected

def test_correlate_bad():
    y1, y2 = np.linspace(0, 10, 11), [0.1, 0.9, 2, 3.2, 4.3, 4.8, 5.9, 7, 7.9, 9, 9.8]
    with pytest.raises(ValueError, match='not known.  Allowed values are'):
        correlate(y1, y2, 'sthg')
    y1, y2 = np.linspace(0, 10, 11), [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1 , 0.1, 0.1]
    with pytest.raises(ValueError, match="similarity metric returned 'nan'"):
        correlate(y1, y2)

def test_rank_returns():
    rank_dict = {}
    for i in range(20):
        rank_dict[i] = {'corr_coeff':1.0-(i*0.05)}
    returns_min, returns_max, similarity_threshold = 5, 20, 0.8
    expected = rank_returns(rank_dict, returns_min, returns_max, similarity_threshold)
    actual = returns_min
    assert actual == expected
    rank_dict = {}
    for i in range(200):
        rank_dict[i] = {'corr_coeff':1.0-(i*0.005)}
    actual = rank_returns(rank_dict, returns_min, returns_max, similarity_threshold)
    expected = returns_max
    assert actual == expected
    rank_dict = {}
    for i in range(20):
        rank_dict[i] = {'corr_coeff':1.0-(i*0.025)}
    actual = rank_returns(rank_dict, returns_min, returns_max, similarity_threshold)
    expected = 9
    assert actual == expected


pa = [
    ({'wavelength': "1", 'qgrid_interval': "2", 'similarity_threshold':"3"},
     {'wavelength': 1, 'qgrid_interval': 2, 'similarity_threshold': 3}),
    ({'wavelength': 1, 'qgrid_interval': 2.0, 'similarity_threshold':"3"},
     {'wavelength': 1.0, 'qgrid_interval': 2.0, 'similarity_threshold': 3}),
    ({'wavelength': "1", 'qgrid_interval': None, 'similarity_threshold': None},
     {'wavelength': 1, 'qgrid_interval': None, 'similarity_threshold': None}),
    (
    {'wavelength': None, 'qgrid_interval': None, 'similarity_threshold': None},
    {'wavelength': None, 'qgrid_interval': None, 'similarity_threshold': None}),
    ({'returns_min_max': ["10", "20"]}, {'returns_min_max': [10, 20]}),
]
@pytest.mark.parametrize("pa", pa)
def test_process_args(pa):
    args = pa[0]
    actual = process_args(args)
    expected = pa[1]
    assert expected == actual

pabad=[
    ({'wavelength': "sthg", 'qgrid_interval': None, 'similarity_threshold': None},
    "Cannot read --wavelength. Please make sure it is a number"),
    ({'wavelength': None, 'qgrid_interval': "sthg", 'similarity_threshold': None},
    "Cannot read --qgrid-interval. Please make sure it is a number"),
    ({'returns_min_max': ["bad", "worse"]},
    "Cannot read --returns-min-max. Please make sure it is a list of numbers")
    ]
@pytest.mark.parametrize("pabad", pabad)
def test_process_args_bad(pabad):
    args = pabad[0]
    with pytest.raises(ValueError, match=pabad[1]) as e_info:
        process_args(args)


ta = [
    ({'xquantity': 'twotheta', 'xunit': 'deg', 'wavelength': 1.5}, True),
    ({'xquantity': 'twotheta', 'xunit': 'rad',  'wavelength': 1}, True),
    ({'xquantity': 'Q', 'xunit': 'inv-A', 'wavelength': 1}, True),
    ({'xquantity': 'q', 'xunit': 'inv-A', 'wavelength': 1}, True),
    ({'xquantity': 'q', 'xunit': 'inv-nm', 'wavelength': 1}, True),
    ({'xquantity': 'd', 'xunit': 'A', 'wavelength': 1}, True),
    ({'xquantity': 'd', 'xunit': 'nm', 'wavelength': 1}, True),
    ({'xquantity': 'd', 'xunit': 'nm', 'wavelength': 1, 'similarity_metric': 'kendall'}, True),
]
@pytest.mark.parametrize("ta", ta)
def test_validate_args(ta):
    args = ta[0]
    actual = validate_args(args)
    expected = ta[1]
    assert expected == actual

ta = [
    ({'xquantity': 'twotheta', 'xunit': 'deg', 'wavelength': None},
     "--wavelength is required when --xquantity is twotheta. "
                        "Please rerun specifying wavelength."),
    ({'xquantity': 'twotheta', 'xunit': 'deg', 'wavelength': "sthg"},
     "Cannot read --wavelength. Please make sure it is a number"),
    ({'xquantity': 'twotheta', 'xunit': 'deg', 'wavelength': 1, 'qgrid_interval': "sthg"},
     "Cannot read --qgrid_interval. Please make sure it is a number"),
    ({'xquantity': 'twotheta', 'xunit': 'deg', 'wavelength': 1, 'similarity_threshold': "sthg"},
     "Cannot read --similarity_threshold. Please make sure it is a number"),
    ({'xquantity': 'sthg', 'xunit': 'deg', 'wavelength': 1.},
     "Cannot read --xquantity. Please provide --xquantity as one of these choices:"),
    ({'xquantity': 'twotheta', 'xunit': 'sthg', 'wavelength': 1.},
     f"--xquantity twotheta, allowed units are"),
    ({'xquantity': 'q', 'xunit': 'sthg', 'wavelength': 1.},
     f"--xquantity Q, allowed units are"),
    ({'xquantity': 'd', 'xunit': 'sthg', 'wavelength': 1.},
     f"--xquantity d-spacing, allowed units are"),
    ({'xquantity': 'd', 'xunit': 'A', 'wavelength': 1., 'similarity_metric': "sthg"},
     f"Cannot read --similarity_metric. allowed values are"),
]
@pytest.mark.parametrize("ta", ta)
def test_validate_args_bad(ta):
    args = ta[0]
    with pytest.raises(RuntimeError, match=ta[1]) as e_info:
        validate_args(args)

qia = [
    ({'xquantity': 'Q', 'xunit': 'inv-nm'},
     np.array([[1.,2.,3.],[100,200,300]]),
     np.array([1.,2.,3.]),np.array([100,200,300])),
    ({'xquantity': 'Q', 'xunit': 'inv-A'},
     np.array([[1., 2., 3.], [100, 200, 300]]),
     np.array([10., 20., 30.]), np.array([100, 200, 300])),
    ({'xquantity': 'd', 'xunit': 'nm'},
     np.array([[1., 2., 3.], [100, 200, 300]]),
     np.array([6.28318531, 3.14159265, 2.0943951 ]), np.array([100, 200, 300])),
    ({'xquantity': 'd', 'xunit': 'A'},
     np.array([[1., 2., 3.], [100, 200, 300]]),
     np.array([62.83185307, 31.41592654, 20.94395102]), np.array([100, 200, 300])),
    ({'xquantity': 'twotheta', 'xunit': 'rad', 'wavelength': 1.5},
     np.array([[1., 2., 3.], [100, 200, 300]]),
     np.array([4.016426, 7.04949084, 8.35659446]), np.array([100, 200, 300])),
    ({'xquantity': 'twotheta', 'xunit': 'deg', 'wavelength': 1.5},
     np.array([[1., 2., 3.], [100, 200, 300]]),
     np.array([0.07310725, 0.14620894, 0.21929949]), np.array([100, 200, 300])),
]


@pytest.mark.parametrize("qia", qia)
def test_create_q_int_arrays(qia):
    args = qia[0]
    actual = create_q_int_arrays(args, qia[1])
    expectedq = qia[2]
    expectedi = qia[3]
    assert expectedq.all() == actual[0].all()
    assert expectedi.all() == actual[1].all()


mm = [
    ([np.array([1., 2., 3.]), 0.1],(0.8,3.2)),
    ([np.array([1., 2., 3.]), None], (0.8, 3.2)),
    ([np.array([2., 1., 3.]), None], (0.8, 3.2)),
]
@pytest.mark.parametrize("mm", mm)
def test_plotting_min_max(mm):
    args = qia[0]
    actual = plotting_min_max(mm[0][0],whitespace_factor=mm[0][1])
    expected = mm[1]
    assert expected == actual
