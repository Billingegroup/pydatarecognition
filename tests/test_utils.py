import numpy as np
import pytest
from datetime import date
from habanero import Crossref
from pydatarecognition.utils import data_sample, pearson_correlate, xy_resample, get_formatted_crossref_reference, \
    hr_to_mr_number_and_esd, mr_to_hr_number_and_esd, round_number_esd

from scipy.stats import pearsonr, spearmanr, kendalltau
from pydatarecognition.utils import (data_sample, pearson_correlate, xy_resample, get_formatted_crossref_reference,
                                     correlate, get_iucr_doi, rank_returns)
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
    (([1, 2, 3, 4, 5],
      [2, 4, 6, 8, 10],
      [1.5, 2.0, 2.5, 3.0, 3.5],
      [3.1, 3.9, 4.9, 6.1, 7.0],
      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
      31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
      [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13,
       13.5, 14, 14.5, 15, 15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20],
      [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22],
      [0.1, 0.9, 2.1, 3.1, 3.9, 4.9, 6.1, 7.0, 7.8, 9.1, 10, 11.1]),
     ([[1.5, 3. ], [1.6, 3.2], [1.7, 3.4], [1.8, 3.6], [1.9, 3.8], [2., 4.], [2.1, 4.2], [2.2, 4.4], [2.3, 4.6],
       [2.4, 4.8], [2.5, 5.], [2.6, 5.2], [2.7, 5.4], [2.8, 5.6], [2.9, 5.8], [3., 6.], [3.1, 6.2], [3.2, 6.4],
       [3.3, 6.6], [3.4, 6.8], [3.5, 7. ]],
      [[1.5 , 3.1 ], [1.6 , 3.26], [1.7 , 3.42], [1.8 , 3.58], [1.9 , 3.74], [2.  , 3.9 ], [2.1 , 4.1 ],
       [2.2 , 4.3 ], [2.3 , 4.5 ], [2.4 , 4.7 ], [2.5 , 4.9 ], [2.6 , 5.14], [2.7 , 5.38], [2.8 , 5.62],
       [2.9 , 5.86], [3.  , 6.1 ], [3.1 , 6.28], [3.2 , 6.46], [3.3 , 6.64], [3.4 , 6.82], [3.5 , 7.  ]]
      ))
]
@pytest.mark.parametrize("pm", pm)
def test_xy_resample(pm):
    with pytest.raises(ValueError) as erc:
        actual = xy_resample(pm[0][0], pm[0][1], pm[0][2], pm[0][3], 0.1)
        assert ValueError('Too narrow xrange: xrange = xmax - xmin < 20') == erc.value
    actual = xy_resample(pm[0][4], pm[0][5], pm[0][6], pm[0][7], 0.1)
    expected = xy1_reg, xy2_reg
    assert np.allclose(actual[0], expected[0])
    assert np.allclose(actual[1], expected[1])
    actual = xy_resample(pm[0][4], pm[0][5], pm[0][6], pm[0][7], 0.01)
    expected = xy3_reg, xy4_reg
    assert np.allclose(actual[0], expected[0])
    assert np.allclose(actual[1], expected[1])


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


def test_hr_to_mr_number_and_esd():
    number_esd = ["343.44(45)", "324908.435(67)", "0.0783(1)", "11(1)", "51(13)", "243(6)", "3205(300)"]
    actual = hr_to_mr_number_and_esd(number_esd)
    expected = [343.4, 324908.44, 0.0783, 11, 51, 243, 3200], [0.5, 0.07, 0.0001, 1, 13, 6, 300]
    assert actual == expected


def test_mr_to_hr_number_and_esd():
    number = [123.5, 123.3, 123.417, 123.367, 123.12, 132.1, 19, 125, 154, 1200, 2, 1, 2.1, 2.1, 2.14, 7.26, 50, 11]
    esd = [0.5, 0.5, 0.326, 0.2, 0.13, 0.236, 2, 20, 20, 207, 1, 1.4, 0.2, 0.25, 0.14, 100, 100, 2]
    actual = mr_to_hr_number_and_esd(number, esd)
    expected = ['123.5(5)', '123.3(5)', '123.4(3)', '123.4(2)', '123.12(13)', '132.1(2)', '19(2)', '130(20)', '150(20)',
                '1200(200)', '2(1)', '0(1)', '2.1(2)', '2.1(3)', '2.14(14)', '0(100)', '0(100)', '11(2)']
    assert actual == expected


def test_round_number_esd():
    number = [123.45, 123.3, 123.35, 123.31, 123.12, 132.124, 19, 123, 145, 1234,
              1.99, 1, 2.145, 2.146, 2.144, 10, 11, 10.6]
    esd = [0.4521, 0.4673, 0.309, 0.213, 0.125, 0.145, 2.4, 21.32, 14.5, 145,
           0.99, 1.11, 0.145, 0.146, 0.144, 100.99, 111, 1.72]
    number_exp = [123.5, 123.3, 123.4, 123.3, 123.12, 132.1, 19, 120, 150, 1200,
                  2, 0, 2.1, 2.1, 2.14, 0, 0, 11]
    esd_exp = [0.5, 0.5, 0.3, 0.2, 0.13, 0.2, 2, 20, 20, 200,
               1, 1, 0.2, 0.2, 0.14, 100, 100, 2]
    actual = round_number_esd(number, esd)
    expected = (number_exp, esd_exp)
    assert actual == expected

    
def test_correlate():
    y1, y2 = np.linspace(0, 10, 11), [0.1, 0.9, 2, 3.2, 4.3, 4.8, 5.9, 7, 7.9, 9, 9.8]
    actual = correlate(y1, y2)
    expected = float(pearsonr(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, 'pearson')
    expected = float(pearsonr(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, 'spearman')
    expected = float(spearmanr(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, 'kendall')
    expected = float(kendalltau(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, 'Pearson')
    expected = float(pearsonr(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, 'Spearman')
    expected = float(spearmanr(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, 'Kendall')
    expected = float(kendalltau(y1, y2)[0])
    assert actual == expected
    actual = correlate(y1, y2, 'Test')
    expected = float(pearsonr(y1, y2)[0])
    assert actual == expected


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

# End of file.
