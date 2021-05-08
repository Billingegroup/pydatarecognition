from pathlib import Path
from cifplotting.io import cif_read, rank_write, user_input_read
from cifplotting.plotters import rank_plot
from cifplotting.utils import data_sample, pearson_correlate

WAVELENGTH = 1.548
parent_path = Path.cwd().resolve().parent
data_path = parent_path / 'data'
cif_dir = data_path / 'cif'
output_path = parent_path / '_output'
powder_data_dir = data_path / 'powder_data'
user_input_file = powder_data_dir / 'sandys_data.txt'
png_path = output_path / 'png'
txt_path = output_path / 'txt'


def main():
    cif_file_list = cif_dir.glob("*.cif")
    folders = [output_path, txt_path, png_path]
    for folder in folders:
        if not folder.exists():
            folder.mkdir()
    #print('-'*80 + '\nInput data file: ' + str(user_input_file.name))
    print('-' * 80)
    print(f"Input data file: {str(user_input_file.name)}")
    print(f"Wavelength: ' {str(WAVELENGTH)} Å.")
    user_data = user_input_read(user_input_file, WAVELENGTH)
    # int_scaled_user = user_data[2]
    new_user_grid = data_sample(user_data)
    cif_file_name_list, r_pearson_list = [], []
    data_dict = {}
    print('\nWorking with files:')
    for cif_file in cif_file_list:
        print(cif_file)
        cif_file_path = Path(cif_file)
        cif_data = cif_read(cif_file_path)
        print('Number of data points: ' + str(len(cif_data[0])) + '\n')
        new_data_grid = data_sample(cif_data)
        # txt = xy_writer(file_path, txt_path, data)
        # plot = cif_plotter(file_path, parent_path, png_path, data)
        r_pearson = pearson_correlate(new_user_grid, new_data_grid)
        cif_file_name_list.append(cif_file_path.stem)
        r_pearson_list.append(r_pearson)
        data_dict[cif_file.stem] = dict([
                                ('tt', cif_data[0]),
                                ('q', cif_data[1]),
                                ('int_exp', cif_data[2]),
                                ('int_scaled', cif_data[3]),
                                ('q_grid', new_data_grid[0]),
                                ('int_grid', new_data_grid[1]),
                                ('r_pearson', r_pearson)])
    cif_pearson_list = list(zip(cif_file_name_list, r_pearson_list))
    cif_rank_pearson_list = sorted(cif_pearson_list, key = lambda x: x[1], reverse=True)
    rank_txt = rank_write(cif_rank_pearson_list, txt_path)
    rank_plots = rank_plot(user_data, cif_rank_pearson_list, data_dict, png_path)
    print('\nA txt file with rankings has been saved into the txt directory, and a plot has been saved into png directory.')

    return None
    # End of function.

if __name__ == "__main__":
    main()

# End of file.
