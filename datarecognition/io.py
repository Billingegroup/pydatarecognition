import numpy as np
from CifFile import StarError

from diffpy.structure.parsers.p_cif import P_cif, _fixIfWindowsPath
import CifFile

def cif_read(cif_file_path):
    '''
    given a cif file-path, reads the cif and returns the cif data
    
    Parameters
    ----------
    cif_file_path  pathlib.Path object
      the path to a valid cif file

    Returns
    -------
    the cif data as a CifFile object
    '''
    cf = CifFile.ReadCif(_fixIfWindowsPath(str(cif_file_path)))
    return cf

def powdercif_pattern_write(cif_file_path, txt_path, data):
    tt = data[0]
    int_exp = data[2]
    txt = []
    for i in range(0, len(tt)):
        if len(str(tt[i])) <= 7:
            txt.append(str(tt[i]) + '\t'*2 + str(int_exp[i]) + '\n')
        elif len(str(tt[i])) > 7:
            txt.append(str(tt[i]) + '\t' + str(int_exp[i]) + '\n')
    file_name = cif_file_path.stem
    txt_file_path = txt_path / file_name
    with open(str(txt_file_path) + '.txt', 'w') as output_file:
        output_file.writelines(txt)
    output_file.close()

    return None
    # End of function.


def user_input_read(user_input_file, wavelength):
    with open(user_input_file) as input_file:
        lines = input_file.readlines()
    input_file.close()
    tt, q, int_exp = [], [], []
    for line in lines:
        tt.append(float(line.split()[0]))
        q.append(float(4 * np.pi * np.sin((np.pi / 180) * float(line.split()[0]) / 2) / wavelength))
        int_exp.append(float(line.split()[1]))
    q_min_round_up = np.ceil(min(q) * 10**2) / 10**2
    q_max_round_down = np.floor(max(q) * 10**2) / 10**2
    int_scaled = []
    # int_max = max(int_exp)
    # for i in range(0, len(int_exp)):
    #     int_scaled.append(int_exp[i] / int_max)
    data_user = [tt, q, int_exp, int_scaled, [q_min_round_up, q_max_round_down]]

    return data_user
    # End of function.


def rank_write(cif_rank_pearson_list, txt_path):
    txt = []
    print('-'*80)
    print('Rank\tFile\t\t\t\t\t\t\t\t\t\tPearson coefficient')
    txt.append('Rank\tFile\t\t\t\t\t\t\t\t\t\tPearson coefficient\n')
    for i in range(0, 10):
        # print(len(str(cif_rank_pearson_list[i][0])))
        if len(cif_rank_pearson_list[i][0]) < 36:
            print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t\t\t'
                  + "{:.4f}".format(cif_rank_pearson_list[i][1]))
            txt.append(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t\t\t'
                       + "{:.4f}".format(cif_rank_pearson_list[i][1]) + '\n')
        if 36 <= len(cif_rank_pearson_list[i][0]) < 40:
            print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t\t'
                  + "{:.4f}".format(cif_rank_pearson_list[i][1]))
            txt.append(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t\t'
                       + "{:.4f}".format(cif_rank_pearson_list[i][1]) + '\n')
        elif len(cif_rank_pearson_list[i][0]) >= 40:
            print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t'
                  + "{:.4f}".format(cif_rank_pearson_list[i][1]))
            txt.append(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t'
                       + "{:.4f}".format(cif_rank_pearson_list[i][1]) + '\n')
    print('-'*80)

    # print('Rank\tIUCr CIF Name\t\t\t\t\tPearson coefficient')
    # txt.append('Rank\tIUCr CIF Name\t\t\t\t\tPearson coefficient')
    # for i in range(0, 10):
    #     if len(cif_rank_pearson_list[i][0]) >= 24:
    #         print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]).split('.')[0] + '\t' + "{:.4f}".format(cif_rank_pearson_list[i][1]))
    #         txt.append(str(i + 1) + '\t' + str(cif_rank_pearson_list[i][0]).split('.')[0] + '\t' + "{:.4f}".format(
    #             cif_rank_pearson_list[i][1]) + '\n')
    #     elif len(cif_rank_pearson_list[i][0]) < 24:
    #         print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]).split('.')[0] + '\t'*2 + "{:.4f}".format(cif_rank_pearson_list[i][1]))
    #         txt.append(str(i + 1) + '\t' + str(cif_rank_pearson_list[i][0]).split('.')[0] + '\t'*2 + "{:.4f}".format(cif_rank_pearson_list[i][1]) + '\n')
    # print('-' * 80)

    with open(txt_path / 'rank.txt', 'w') as output_file:
        output_file.writelines(txt)
    output_file.close()

    return None
    # End of function.
