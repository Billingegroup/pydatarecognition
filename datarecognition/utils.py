import numpy as np
import scipy.stats
from scipy.interpolate import interp1d

def data_sample(cif_data):
    tt = cif_data[0]
    q = cif_data[1]
    int_exp = cif_data[2]
    int_scaled = cif_data[3]
    q_min_round_up = cif_data[4][0]
    q_max_round_down = cif_data[4][1]
    int_intpol = interp1d(np.array(q), np.array(int_exp), kind='cubic')
    q_step_grid = 0.005
    q_grid = np.arange(q_min_round_up, q_max_round_down, q_step_grid)
    int_grid = int_intpol(q_grid)
    new_data_grid = [q_grid, int_grid]

    return new_data_grid
    # End of function.


def pearson_correlate(new_user_grid, new_data_grid):
    q_user = new_user_grid[0]
    int_user = new_user_grid[1]
    q_data = new_data_grid[0]
    int_data = new_data_grid[1]
    min_q = max(np.amin(q_user), np.amin(q_data))
    max_q = min(np.amax(q_user), np.amax(q_data))
    for i in range(0, len(q_user)):
        if q_user[i] <= min_q:
            min_q_user_index = i
        elif q_user[i] <= max_q:
            max_q_user_index = i + 1
    for i in range(0, len(q_data)):
        if q_data[i] <= min_q:
            min_q_data_index = i
        elif q_data[i] <= max_q:
            max_q_data_index = i + 1
    pearson = scipy.stats.pearsonr(np.array(int_user)[min_q_user_index:max_q_user_index],
                                   np.array(int_data)[min_q_data_index:max_q_data_index])
    r_pearson = pearson[0]
    p_pearson = pearson[1]

    return r_pearson
    # End of function.
