# Import section
import sys
import os
import glob
from pathlib import Path
import matplotlib.pyplot as plt

# Data section

def cif_reader(file_path):
    with open(file_path, 'r') as input_file:
        lines = input_file.readlines()
    input_file.close

    for i in range(0, len(lines)):
        if '_pd_proc_intensity_bkg_calc' in lines[i]:
            start = i + 2

        elif '_pd_proc_number_of_points' in lines[i]:
            end = i

    tt, int = [], []
    for i in range(start, end):
        tt.append(float(lines[i].split()[1]))
        int.append(float(lines[i].split()[2].split('(')[0]))

    data = []
    data.append(tt)
    data.append(int)

    return data
    # End fo function.

def xy_writer(file_path, txt_path, data):
    tt = data[0]
    int = data[1]

    txt = []
    for i in range(0, len(tt)):
        if len(str(tt[i])) <= 7:
            txt.append(str(tt[i]) + ('\t')*2 + str(int[i]) + '\n')
        elif len(str(tt[i])) > 7:
            txt.append(str(tt[i]) + '\t' + str(int[i]) + '\n')

    file_name = file_path.stem
    txt_file_path = txt_path / file_name

    with open(str(txt_file_path) + '.txt', 'w') as output_file:
        output_file.writelines(txt)
    output_file.close()

    return None
    # End of function.

def cif_plotter(file_path, png_path, data):
    file_name = file_path.resolve().stem
    file_name = str(file_name)
    plot_file_name = file_name + '.png'

    tt = data[0]
    int = data[1]

    fig_size = (12,4)
    fig, ax = plt.subplots(dpi=300, figsize=fig_size)

    color_list = ['#0B3C5D', '#B82601', '#1c6b0a', '#328CC1', '#062F4F',
                  '#D9B310', '#984B43', '#76323F', '#626E60', '#AB987A',
                  '#C09F80']

    # color_list = [blue, red, green, lightblue, darkblue,
    #               yellow, darkred, bordeaux, olivegreen, yellowgreen,
    #               brownorange]

    plt.plot(tt, int, c=color_list[0], linewidth=1)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.xlabel(r"2$\theta$ $[\degree]$")
    plt.ylabel(r"$I$ $[\mathrm{counts}]$")
    plt.xlim(min(tt), max(tt))
    plt.ylim(min(int), max(int))
    plt.savefig(png_path / plot_file_name, bbox_inches='tight')
    plt.close()

    return None
    # End fo function.

def main():
    src_path = Path.cwd()
    parent_path = src_path.resolve().parent
    data_path = parent_path / 'data'
    txt_path = parent_path / 'txt'
    png_path = parent_path / 'png'

    folders = [txt_path, png_path]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # file_path = data_path / INPUT_FILE_NAME

    file_list = glob.glob(str(data_path) + '/**.cif')

    for file in file_list:
        file_path = Path(file)
        data = cif_reader(file_path)
        txt = xy_writer(file_path, txt_path, data)
        plot = cif_plotter(file_path, png_path, data)

    return None
    # End of function.

if __name__ == "__main__":
    main()

# End of file.
