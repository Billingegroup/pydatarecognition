# Import section
import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt
# import matplotlib as mpl
# from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
import numpy as np
import scipy.stats
from scipy.interpolate import interp1d
# import json

# Data section
def cif_reader(file_path):

    # Open cif file and read lines.
    with open(file_path, 'r') as input_file:
        lines = input_file.readlines()
    input_file.close

    # The the indices for the lines containing the probe and wavelength
    # and the lines where the data starts and ends.
    for i in range(0, len(lines)):
        if '_diffrn_radiation_probe' in lines[i]:
            probe = lines[i].split()[-1]

        elif '_diffrn_radiation_wavelength' in lines[i]:
            wavelength = float(lines[i].split()[-1])

        elif '_pd_proc_intensity_bkg_calc' in lines[i]:
            start = i + 2

        elif '_pd_proc_number_of_points' in lines[i]:
            end = i

    # Append twotheta and intensity values to lists.
    # Calculate q-values and append to list.
    tt, int_exp, q = [], [], []
    for i in range(start, end):
        tt.append(float(lines[i].split()[1]))
        q.append(4 * np.pi * np.sin((np.pi / 180) * float(lines[i].split()[1]) / 2) / wavelength)
        int_exp.append(float(lines[i].split()[2].split('(')[0]))

    # Getting the minimum and maximum q-values, rounded to two digits.
    q_min_round_up = np.ceil(min(q) * 10**2) / 10**2
    q_max_round_down = np.floor(max(q) * 10**2) / 10**2

    # Scale the intensities with respect to the maximum intensity
    # and append to list.
    int_scaled = []
    for i in range(0, len(int_exp)):
        int_scaled.append(int_exp[i] / max(int_exp))

    # plt.plot(q, int_scaled)
    # plt.xlabel(r"$Q$ $[\mathrm{\AA^{-1}}]$")
    # plt.ylabel(r"$I$ $[\mathrm{a.u.}]$")
    # plt.show()
    # sys.exit()

    # Append values to be returned to data list that is returned.
    data = []
    data.append(tt)
    data.append(q)
    data.append(int_exp)
    data.append(int_scaled)
    data.append([q_min_round_up, q_max_round_down])
    data.append(probe)

    return data
    # End fo function.

def xy_writer(file_path, txt_path, data):

    # Unpacking twotheta and intensity lists from data list.
    tt = data[0]
    int_exp = data[2]

    # Appending lines to txt list.
    txt = []
    for i in range(0, len(tt)):
        if len(str(tt[i])) <= 7:
            txt.append(str(tt[i]) + ('\t')*2 + str(int_exp[i]) + '\n')
        elif len(str(tt[i])) > 7:
            txt.append(str(tt[i]) + '\t' + str(int_exp[i]) + '\n')

    # Getting the file name without file extension and setting up txt path.
    file_name = file_path.stem
    txt_file_path = txt_path / file_name

    # Writing txt file.
    with open(str(txt_file_path) + '.txt', 'w') as output_file:
        output_file.writelines(txt)
    output_file.close()

    return None
    # End of function.

def cif_plotter(file_path, parent_path, png_path, data, bg_mpl_style=None):

    # Getting the file name and setting up the plot file name.
    file_name = str(file_path.resolve().stem)
    plot_file_name = file_name + '.png'

    # Unpacking twotheta and intensity lists from data list.
    tt = data[0]
    int_exp = data[1]

    # mpl.rcParams.update(mpl.rcParamsDefault)
    # plt.style.use(os.path.join(parent_path, "utils","billinge.mplstyle"))

    # Plot style used.
    plt.style.use(bg_mpl_style)

    # Making figure using subplots.
    fig, ax = plt.subplots(dpi=300, figsize=(12,4))

    # Plotting twotheta vs. intensity.
    ax.plot(tt, int_exp, linewidth=1)

    # Setting the y-axis to scientific notation.
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    # Setting labels for the axes.
    ax.set_xlabel(r"2$\theta$ $[^{\circ}]$")#, labelpad=5)
    ax.set_ylabel(r"$I$ $[\mathrm{counts}]$")#, labelpad=5)

    # Setting the limits for the axes.
    plt.xlim(min(tt), max(tt))
    # plt.ylim(min(int), max(int))

    # Saving figure to png file and closing figure.
    plt.savefig(png_path / plot_file_name, bbox_inches='tight')
    plt.close()

    return None
    # End fo function.

def user_input(user_input_file, wavelength):

    # Opening file and reading lines.
    with open(user_input_file) as input_file:
        lines = input_file.readlines()
    input_file.close()

    # Appending twotheta and intensity values to lists.
    # Calculating q-values and appending to list.
    tt, q, int_exp = [], [], []
    for line in lines:
        tt.append(float(line.split()[0]))
        q.append(float(4 * np.pi * np.sin((np.pi / 180) * float(line.split()[0]) / 2) / wavelength))
        int_exp.append(float(line.split()[1]))

    # Getting minimum and maximum q-values rounded to two digits.
    q_min_round_up = np.ceil(min(q) * 10**2) / 10**2
    q_max_round_down = np.floor(max(q) * 10**2) / 10**2

    # Calculating the scaled intensity with respect to the maximum intensity
    # and appending to list.
    int_scaled = []
    for i in range(0, len(int_exp)):
        int_scaled.append(int_exp[i] / max(int_exp))

    # Appending data to be returned to list.
    data_user = []
    data_user.append(tt)
    data_user.append(q)
    data_user.append(int)
    data_user.append(int_scaled)
    data_user.append([q_min_round_up, q_max_round_down])

    return data_user
    # End of function.

def data_sampler(data):

    # Unpacking data and minimum and maximum q-values.
    q = data[1]
    int_scaled = data[3]
    q_min_round_up = data[4][0]
    q_max_round_down = data[4][1]

    # Interpolation of data using cubic kind.
    int_intpol = interp1d(np.array(q), np.array(int_scaled), kind='cubic')

    # Step size for the new q-grid.
    q_step_grid = 0.005

    # Making new q-grid.
    q_grid = np.arange(q_min_round_up, q_max_round_down, q_step_grid)

    # Getting the intensity values corresponding to the new q-grid.
    int_grid = int_intpol(q_grid)

    # Appending new q and intensity values to be returned.
    new_data_grid = []
    new_data_grid.append(q_grid)
    new_data_grid.append(int_grid)

    return new_data_grid
    # End of function.

def pearson_correlator(new_user_grid, new_data_grid):

    # Unpacking user data on new grid.
    q_user = new_user_grid[0]
    int_user = new_user_grid[1]

    # Unpacking cif data on new grid.
    q_data = new_data_grid[0]
    int_data = new_data_grid[1]

    # Getting the minimum and maximum q-values.
    min_q = max(np.amin(q_user), np.amin(q_data))
    max_q = min(np.amax(q_user), np.amax(q_data))

    # Getting the indices for the minimum and maximum q-values
    # for the user and cif data.
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

    # Estimating the Pearson correlation coefficient and the p-value.
    pearson = scipy.stats.pearsonr(np.array(int_user)[min_q_user_index:max_q_user_index],
                                   np.array(int_data)[min_q_data_index:max_q_data_index]
                                   )

    # Pearson coefficient and p-value.
    r_pearson = pearson[0]
    p_pearson = pearson[1]

    return r_pearson
    # End of function.

def rank_plotter(user_data, sorted_zipped_list, data_dict, png_path):

    # Getting the top 5 ranked cif data from dictionary and appending to lists.
    q, int_scaled = [], []
    for i in range(0, 5):
        file = sorted_zipped_list[i][0]
        for key in data_dict:
            if key == file:
                q.append(data_dict[key]['q'])
                int_scaled.append(data_dict[key]['int_scaled'])

    # Making figure using subplots.
    fig, axs = plt.subplots(6, 1, sharex=True, sharey=True, figsize=(8,4), dpi=300)

    # Setting x-limit.
    plt.xlim(min(user_data[1]), max(user_data[1]))

    # Setting y-ticks.
    plt.yticks([])

    # Add a big axis, hide frame.
    fig.add_subplot(111, frameon=False)

    # Hide ticks and tick labels on the big axis.
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)

    # Setting axis labels.
    plt.xlabel(r"$Q$ $[\mathrm{\AA}^{-1}]$", fontsize=16)
    plt.ylabel(r"$I$ $[\mathrm{arb.u.}]$", fontsize=16, labelpad=-10)

    # plt.style.use(bg_mpl_style)
    colors = ["#0B3C5D", "#B82601", "#1c6b0a", "#328CC1", "#062F4F", "#D9B310",
              "#984B43", "#76323F", "#626E60", "#AB987A", "#C09F80"
              ]
    # Plotting user data topmost, and then ranked data in descending order.
    axs[0].plot(user_data[1], user_data[3], c=colors[0], lw=0.5)
    axs[0].text(0.89*max(user_data[1]), 0.7, 'User data')
    for i in range(1, 6):
        axs[i].plot(q[i-1], int_scaled[i-1], c=colors[i], lw=0.5)
        axs[i].text(0.89*max(user_data[1]), 0.7, 'Rank: ' + str(i))
        # axs[i].set_xlim(min(user_data[1]), max(user_data[1]))

    # Saving figure as png file and closing plot.
    plt.savefig(png_path / 'rank_plot.png', bbox_inches='tight')
    plt.close()

    return None
    # End of function.

def rank_writer(sorted_zipped_list, txt_path):

    # Printing top 10 ranked cif files to terminal
    # and writing to txt file.
    txt = []
    print('-'*80)
    print('Rank\tFile\t\t\t\t\t\tPearson coefficient')
    txt.append('Rank\tFile\t\t\t\t\t\tPearson coefficient\n')
    for i in range(0, 10):
        if len(sorted_zipped_list[i][0]) < 40:
            print(str(i + 1) + '\t' + str(sorted_zipped_list[i][0]) + '\t\t' + "{:.4f}".format(sorted_zipped_list[i][1]))
            txt.append(str(i + 1) + '\t' + str(sorted_zipped_list[i][0]) + '\t\t' + "{:.4f}".format(sorted_zipped_list[i][1]) + '\n')

        elif len(sorted_zipped_list[i][0]) >= 40:
            print(str(i + 1) + '\t' + str(sorted_zipped_list[i][0]) + '\t' + "{:.4f}".format(sorted_zipped_list[i][1]))
            txt.append(str(i + 1) + '\t' + str(sorted_zipped_list[i][0]) + '\t' + "{:.4f}".format(sorted_zipped_list[i][1]) + '\n')

    print('-'*80)

    with open(txt_path / 'rank.txt', 'w') as output_file:
        output_file.writelines(txt)
    output_file.close()

    return None
    # End of function.

def main():

    # Path for src directory.
    src_path = Path.cwd()

    # Parent directory.
    parent_path = src_path.resolve().parent

    # Path for data directory.
    data_path = parent_path / 'data'

    # List of cif files within data directory.
    file_list = data_path.glob("*.cif")

    txt_path = parent_path / 'txt'
    png_path = parent_path / 'png'

    folders = [txt_path, png_path]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Path to input file from user and wavelength used for user data.
    user_input_file = parent_path / 'sandys_data.txt'
    wavelength = 1.548

    print('-'*80 + '\nInput data file: ' + str(user_input_file.name))
    print('Wavelength: ' + str(wavelength) + ' Å.')
    # Extracting data from user file.
    user_data = user_input(user_input_file, wavelength)

    # Getting the scaled intensities from the user data.
    int_scaled_user = user_data[2]

    # Sampling the user data on a new grid.
    new_user_grid = data_sampler(user_data)

    # Dictionary for filenames, q-values, and scaled intensities on
    # new grid for cif files.
    data_dict = {}

    # Lists for filenames and Pearson coefficients to be printed.
    file_name_list, r_pearson_list = [], []

    # Printing to terminal.
    print('\nWorking with files:')

    # Looping through list of cif files.
    for file in file_list:
        # Printing the file name.
        print(file)

        # Getting the path for the cif file.
        file_path = Path(file)

        # Extracting data from the cif file.
        data = cif_reader(file_path)
        print('Number of data points: ' + str(len(data[0])) + '\n')

        # Sampling Q-values and scaled intensities on new grid.
        new_data_grid = data_sampler(data)

        # Writing .txt file with twotheta and intensity values from cif file.
        # txt = xy_writer(file_path, txt_path, data)

        # Plotting twotheta and intensities from cif file.
        # plot = cif_plotter(file_path, parent_path, png_path, data)

        # Calculating the Pearson coefficient.
        r_pearson = pearson_correlator(new_user_grid, new_data_grid)

        # Appending name of cif file to list of filenames.
        file_name_list.append(file_path.stem)

        # Appending Pearson coefficient to list of of Pearson coefficients.
        r_pearson_list.append(r_pearson)

        # Dictionary with Q-values, scaled intensities, and Pearson coefficient
        # for all cif files.
        data_dict[file.stem] = dict([
                                ('q', data[1]),
                                ('int_scaled', data[3]),
                                ('q_grid', new_data_grid[0]),
                                ('int_grid', new_data_grid[1]),
                                ('r_pearson', r_pearson)
                                ])

    # Zipping cif filenames and their corresponding Pearson coefficients.
    zipped_list = list(zip(file_name_list, r_pearson_list))

    # Sorting the zipped lists in ascending order with respect to the Pearson
    # coefficient.
    sorted_zipped_list = sorted(zipped_list, key = lambda x: x[1], reverse=True)

    # Writing dictionary with cif data to text file.
    # with open(parent_path / 'cif_dict.txt', 'w') as output_file:
    #     output_file.write(json.dumps(data_dict))
    # output_file.close()

    # Writing top 5 rank to txt file.
    rank_txt = rank_writer(sorted_zipped_list, txt_path)

    # Plotting user data and top five rank and saving to png file.
    rank_plots = rank_plotter(user_data, sorted_zipped_list, data_dict, png_path)
    print('\nA txt file with rankings has been saved into the txt directory, and a plot has been saved into png directory.')

    return None
    # End of function.

if __name__ == "__main__":
    main()

# End of file.
