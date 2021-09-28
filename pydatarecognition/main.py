import os
from pathlib import Path
import numpy as np
import scipy.stats
from skbeam.core.utils import twotheta_to_q
from pydatarecognition.cif_io import cif_read, rank_write, user_input_read, cif_read_ext, json_dump
from pydatarecognition.utils import xy_resample
from pydatarecognition.plotters import rank_plot
import argparse
import sys
############################################################################################
# TESTFILE = 3 # FIXME Use cli to parse this information instead.
# if TESTFILE == 1:
#     # test cif, which IS present within the test set
#     # together with cifs from same paper
#     # x-ray data
#     # bm5088150212-01-betaTCPsup2.rtv.combined.cif
#     WAVELENGTH = 0.1540598
#     USER_INPUT_FILE = 'sandys_data_1.txt'
#     XTYPE = 'twotheta'
# elif TESTFILE == 2:
#     # test cif, which IS present within the test set
#     # no other cifs from the same paper
#     # x-ray data
#     # br2109Isup2.rtv.combined.cif
#     WAVELENGTH = 0.154175
#     USER_INPUT_FILE = 'sandys_data_2.txt'
#     XTYPE = 'twotheta'
# elif TESTFILE == 3:
#     # test cif, which is NOT present within the test set
#     # no other cifs from the same paper
#     # neutron data
#     # aj5301cubic_1_NDsup19.rtv.combined.cif
#     WAVELENGTH = 0.15482
#     USER_INPUT_FILE = 'sandys_data_3.txt'
#     XTYPE = 'twotheta'
STEPSIZE_REGULAR_QGRID = 10**-3
############################################################################################


def main():
    XCHOICES = ['Q','twotheta','d']
    XUNITS = ["inv-A", "inv-nm", "deg", "rad", "A", "nm"]
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', required=True, help="path to the input data-file. Path can be relative from the current "
                                             "location, e.g., ./my_data_dir/my_data_filename.xy")
    parser.add_argument('--xquantity', required=True, choices=XCHOICES,
                        help=f"Independent variable quantity of the input data, from {*XCHOICES,}. By default units "
                             f"are {*XUNITS,}, respectively")
    parser.add_argument('--xunit', required=True, choices=XUNITS,
                        help=f"Units for the independent variable quantity of the input data if different from the "
                             f"default, from {*XUNITS,}")
    parser.add_argument('-o','--output', help="path to output files. Path can be relative from the current "
                                             "location, e.g., ./my_data_dir/")
    parser.add_argument('-w','--wavelength', help="wavelength of the radiation in angstrom units. Required if "
                                                  "xquantity is twotheta")
    parser.add_argument('--jsonify', action='store_true', help="dumps cifs into jsons")

    args = parser.parse_args()
    if args.xquantity == 'twotheta' and not args.wavelength:
        parser.error('--wavelength is required when --xquantity is twotheta')

    # These need to be inside main for this to run from an IDE like PyCharm
    # and still find the example files.
    parent_dir = Path.cwd()
    cif_dir = parent_dir / 'cifs'
    user_input = Path(args.input).resolve()
    ciffiles = cif_dir.glob("*.cif")
    doifile = cif_dir / 'iucrid_doi_mapping.txt'
    if isinstance(args.output, type(None)):
        user_output = Path.cwd()
    else:
        user_output = Path(args.output).resolve()
    output_dir = user_output / '_output'
    folders = [output_dir]
    for folder in folders:
        if not folder.exists():
            folder.mkdir()
    dois = np.genfromtxt(doifile, dtype='str')
    doi_dict = {}
    for i in range(len(dois)):
        doi_dict[dois[i][0]] = dois[i][1]
    frame_dashchars = '-'*85
    newline_char = '\n'
    print(f'{frame_dashchars}{newline_char}Input data file: {user_input.name}{newline_char}'
          f'Wavelength: {args.wavelength} Å.{newline_char}{frame_dashchars}')
    userdata = user_input_read(user_input)
    if args.xquantity == 'twotheta':
        user_twotheta, user_intensity = userdata[0,:], userdata[1:,][0]
        user_q = twotheta_to_q(np.radians(user_twotheta), float(args.wavelength)/10)
        user_qmin, user_qmax = np.amin(user_q), np.amax(user_q)
    cifname_ranks, r_pearson_ranks, doi_ranks = [], [], []
    user_dict, cif_dict = {}, {}
    log = 'pydatarecognition log\nThe following files were skipped:\n'
    print('Working with CIFs:')
    if args.jsonify:
        for ciffile in ciffiles:
            print(ciffile.name)
            ciffile_path = Path(ciffile)
            json_data = cif_read_ext(ciffile_path, 'json')
            pre = Path(ciffile).stem
            json_dump(json_data, str(output_dir/pre) + ".json")
    else:
        for ciffile in ciffiles:
            print(ciffile.name)
            ciffile_path = Path(ciffile)
            pcd = cif_read(ciffile_path)
            try:
                data_resampled = xy_resample(user_q, user_intensity, pcd.q, pcd.intensity, STEPSIZE_REGULAR_QGRID)
                pearson = scipy.stats.pearsonr(data_resampled[0][:,1], data_resampled[1][:,1])
                r_pearson = pearson[0]
                p_pearson = pearson[1]
                cifname_ranks.append(ciffile.stem)
                r_pearson_ranks.append(r_pearson)
                doi = doi_dict[pcd.iucrid]
                doi_ranks.append(doi)
                cif_dict[str(ciffile.stem)] = dict([
                            ('intensity', pcd.intensity),
                            ('q', pcd.q),
                            ('qmin', np.amin(pcd.q)),
                            ('qmax', np.amax(pcd.q)),
                            ('q_reg', data_resampled[1][:,0]),
                            ('intensity_resampled', data_resampled[1][:,1]),
                            ('r_pearson', r_pearson),
                            ('p_pearson', p_pearson),
                            ('doi', doi),
                        ])
            except AttributeError:
                print(f"{ciffile.name} was skipped.")
                log += f"{ciffile.name}\n"
        user_dict[str(user_input.stem)] = dict([
            ('twotheta', userdata[:, 0]),
            ('intensity', userdata[:, 1]),
            ('q', user_q),
            ('q_min', user_qmin),
            ('q_max', user_qmax),
        ])
        cif_rank_pearson = sorted(list(zip(cifname_ranks, r_pearson_ranks, doi_ranks)), key = lambda x: x[1], reverse=True)
        ranks = [{'IUCrCIF': cif_rank_pearson[i][0],
                  'score': cif_rank_pearson[i][1],
                  'doi': cif_rank_pearson[i][2]} for i in range(len(cif_rank_pearson))]
        rank_txt = rank_write(ranks, output_dir)
        print(f'{frame_dashchars}{newline_char}{rank_txt}{frame_dashchars}')
        rank_plots = rank_plot(data_resampled[0][:,0], data_resampled[0][:, 1], cif_rank_pearson, cif_dict, output_dir)
        print(f'A txt file with rankings has been saved to the txt directory,{newline_char}'
              f'and a plot has been saved to the png directory.{newline_char}{frame_dashchars}')
        with open((output_dir / "pydatarecognition.log"), "w") as o:
            o.write(log)

    return None

if __name__ == "__main__":
    # in Pycharm (and probably other IDEs) it runs main in place, so if so
    # detect this and move to the examples folder where it can find the data
    cwd = Path().cwd()
    relpath = cwd / ".." / "docs" / "examples"
    if cwd.parent.name == "pydatarecognition" and cwd.parent.parent.name != "pydatarecognition":
        os.chdir(relpath)

    main()

# End of file.
