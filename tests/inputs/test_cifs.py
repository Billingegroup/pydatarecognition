# Put cif file patterns here to test cif readers and cif parsers
#
# the pattern is as follows
# testciffiles_contents_expecteds = [(file_1_contents_as_string, file1_expected_as_dict),
#                          (file_2_contents_as_string, file1_expected_as_dict),
#                          ...
#                         ]
#
# where the expected outputs has one block with a blockname, a list of block
#    items and a list of loop items.  Block items are for simple cif_key, cif_value
#    pairs and loop items are themselves a dict containing lists of keys and values
import numpy

testciffiles_contents_expecteds = [
    ("\
data_cubic_1_ND\n\
\n\
_diffrn_radiation_probe                neutrons\n\
_diffrn_radiation_wavelength            1.5482\n\
\n\
loop_\n\
_pd_proc_point_id\n\
_pd_proc_2theta_corrected\n\
_pd_proc_intensity_total\n\
_pd_calc_intensity_total\n\
_pd_proc_intensity_bkg_calc\n\
 \n\
   177    10.0413    2037(166)          1886.0148         1886.0148\n\
   178    10.0913    2212(172)          1886.0148         1886.0148\n\
   179    10.1413    2155(169)          1886.0148         1886.0148\n\
"
     ,
     {"wavelength": 0.15482,
      "q": numpy.array([7.10336591, 7.13864541, 7.17392354]),
      "intensity": numpy.array([2037, 2212, 2155]),
      "ttheta": numpy.array([10.0413, 10.0913, 10.1413]),
      "iucrid": "test_c"}
     ),
    ("\
     data_cubic_1_ND\n\
     \n\
     _diffrn_radiation_probe                neutrons\n\
     \n\
     loop_\n\
     _pd_proc_point_id\n\
     _pd_proc_2theta_corrected\n\
     _pd_proc_intensity_total\n\
     _pd_calc_intensity_total\n\
     _pd_proc_intensity_bkg_calc\n\
      \n\
        177    10.0413    2037(166)          1886.0148         1886.0148\n\
        178    10.0913    2212(172)          1886.0148         1886.0148\n\
        179    10.1413    2155(169)          1886.0148         1886.0148\n\
     ",
     {"iucrid": "test_c",
      "intensity": numpy.array([2037, 2212, 2155]),
      "ttheta": numpy.array([10.0413, 10.0913, 10.1413])}
     )
]

# {'block_name': 'cubic_1_ND',
#  "block_items": [("_diffrn_radiation_probe", "neutrons"),
#                  ('_diffrn_radiation_wavelength', '1.5482')
#                  ],
#  "loop_items": [{"keys": ["_pd_proc_point_id",
#                           "_pd_proc_2theta_corrected",
#                           "_pd_proc_intensity_total",
#                           "_pd_calc_intensity_total",
#                           "_pd_proc_intensity_bkg_calc"],
#                  "values": [["177", "178", "179"],
#                             ["10.0413", "10.0913", "10.1413"],
#                             ["2037(166)", "2212(172)", "2155(169)"],
#                             ["1886.0148", "1886.0148", "1886.0148"],
#                             ["1886.0148", "1886.0148", "1886.0148"]
#                             ]
#                  }
#                 ]}
