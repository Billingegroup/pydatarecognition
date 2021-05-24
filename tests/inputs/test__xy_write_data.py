# Put xy data here to test _xy_write().
#
# the pattern is as follows
# _xy_write_contents_expecteds = [(xy_data_as_list, xy_data_as_string),
#                                 (xy_data_as_list, xy_data_as_string),
#                                 ...
#                                 ]
# where the expected outputs are strings.

test__xy_write_data_contents_expecteds = [
    (([1.0, 2, 3.2],
      [4, 5.5, 6]),
       '1.000000000000000000e+00\t4.000000000000000000e+00\n' \
       '2.000000000000000000e+00\t5.500000000000000000e+00\n' \
       '3.200000000000000178e+00\t6.000000000000000000e+00\n'),
]
