import numpy as np
import yaml
import CifFile
from diffpy.structure.parsers.p_cif import _fixIfWindowsPath
from diffpy.utils.parsers.loaddata import loadData
from pydatarecognition.powdercif import PowderCif
from pydatarecognition.utils import get_formatted_crossref_reference

DEG = "deg"

def cif_read(cif_file_path):
    '''
    given a cif file-path, reads the cif and returns the cif data
    
    Parameters
    ----------
    cif_file_path  pathlib.Path object
      the path to a valid cif file

    Returns
    -------
    the cif data as a pydatarecognition.powdercif.PowderCif object
    '''
    cache = cif_file_path.parent / "_cache"
    if not cache.exists():
        cache.mkdir()
    acache = cache / f"{cif_file_path.stem}.npy"
    mcache = cache / f"{cif_file_path.stem}.yml"

    cachegen = cache.glob("*.npy")
    index = list(set([file.stem for file in cachegen]))
    if cif_file_path.stem in index:
        print("Getting from Cache")
        qi = np.load(acache, allow_pickle=True)
        q = qi[0]
        intensity = qi[1]
        with open(mcache) as o:
            meta = yaml.safe_load(o)
        po = PowderCif(cif_file_path.stem[0:6], "invnm", q, intensity)
    else:
        print("Getting from Cif File")
        cifdata = CifFile.ReadCif(_fixIfWindowsPath(str(cif_file_path)))
        cif_twotheta = np.char.split(cifdata[cifdata.keys()[0]]['_pd_proc_2theta_corrected'], '(')
        cif_twotheta = np.array([float(e[0]) for e in cif_twotheta])
        cif_intensity = np.char.split(cifdata[cifdata.keys()[0]]['_pd_proc_intensity_total'], '(')
        cif_intensity = np.array([float(e[0]) for e in cif_intensity])
        for key in cifdata.keys():
            wavelength_kwargs = {}
            cif_wavelength = cifdata[key].get('_diffrn_radiation_wavelength')
            if isinstance(cif_wavelength, list):
                wavelength_kwargs['wavelength'] = float(cif_wavelength[0]) # FIXME Handle lists
                wavelength_kwargs['wavel_units'] = "ang"
                break # FIXME Don't just go with first instance of wavelength.
            elif isinstance(cif_wavelength, str):
                wavelength_kwargs['wavelength'] = float(cif_wavelength)
                wavelength_kwargs['wavel_units'] = "ang"
                break # FIXME Don't just go with first instance of wavelength.
            else:
                pass
        if not cif_wavelength:
            wavelength_kwargs['wavelength'] = None
        po = PowderCif(cif_file_path.stem[0:6],
                       DEG, cif_twotheta, cif_intensity,
                       **wavelength_kwargs
                       )
    try:
        po.q
        with open(acache, "wb") as o:
            np.save(o, np.array([po.q, po.intensity]))
        with open(mcache, "w") as o:
            yaml.safe_dump({"iucrid": str(po.iucrid),
                            "wavelength": po.wavelength},o)
    except AttributeError:
        with open(acache, "wb") as o:
            np.save(o, np.array([None, po.intensity]))
        with open(mcache, "w") as o:
            yaml.safe_dump({"iucrid": str(po.iucrid),
                            "wavelength": po.wavelength}, o)

    return po


def _xy_write(output_file_path, x_vals, y_vals):
    '''
    given an output file path, x- and y-arrays, a two-column text file with x- and y-values is written.

    Parameters
    ----------
    output_file_path pathlib.Path object
      the path for the output file
    x_vals iterable
      iterable containing x values as floats or integers
    y_vals iterable
      iterable containing y values as floats or integers

    Returns
    -------
    None
    '''
    xy_array = np.column_stack((np.array(x_vals), np.array(y_vals)))
    np.savetxt(output_file_path, xy_array, delimiter='\t', newline='\n', encoding='utf8')

    return


def user_input_read(user_input_file_path):
    '''
    given a user input file path, reads the user data into ndarrays.

    Parameters
    ----------
    user_input_file_path pathlib.Path object
      the path to a user input file containing diffraction data

    Returns
    -------
    user_data  ndarray object
      ndarray with the columns of the user input input file. Dimensions will depend on the number of columns.
    '''
    user_data = loadData(user_input_file_path).T

    return user_data


def rank_write(cif_ranks, output_path):
    '''
    given a list of dicts of IUCr CIFs, scores, and DOIs together with a path to the output dir,
    writes a .txt file with ranks, scores, IUCr CIFs, and DOIs.

    Parameters
    ----------
    cif_ranks  list object
      a list of dicts of IUCr CIF names, scores, and DOIs, ranked according to their score
    output_path  pathlib.Path object
      path to output directory of the .txt file that will be written as rank.txt

    -------
    rank_doi_score_txt string object
      a string containing ranks, scores, IUCr CIFs, and DOIs that are written to a txt file.
      the string is returned, so that it can e.g. be printed to the terminal.
    '''
    tablen_print = 4
    tablen_write = 8
    # strlen = [len(cif_ranks[i]['IUCrCIF']) for i in range(len(cif_ranks))]
    # strlen_max = max(strlen)
    # char_max_print = strlen_max - (strlen_max % tablen_print) + tablen_print
    # char_max_write = strlen_max - (strlen_max % tablen_write) + tablen_write
    # tabs_print = [int(((char_max_print - (strlen[i] - (strlen[i] % tablen_print) + tablen_print)) / tablen_print) + 1)
    #               for i in range(len(strlen))]
    # tabs_write = [int(((char_max_write - (strlen[i] - (strlen[i] % tablen_write) + tablen_write)) / tablen_write) + 1)
    #               for i in range(len(strlen))]

    tab_char = '\t'
    rank_doi_score_txt_print = f"Rank\tScore\tDOI{tab_char*7}Reference\n"
    rank_doi_score_txt_write = f"Rank\tScore\tDOI{tab_char*7}Reference\n"
    for i in range(len(cif_ranks)):
        rank_doi_score_txt_write += f"{i+1}\t{cif_ranks[i]['score']:.4f}\t{cif_ranks[i]['doi']}\t" \
                                    f"{get_formatted_crossref_reference(cif_ranks[i]['doi'])[0].encode('cp850','replace').decode('cp850')}\n"
        rank_doi_score_txt_print += f"{i+1}{tab_char*2}{cif_ranks[i]['score']:.4f}\t{cif_ranks[i]['doi']}\t" \
                                    f"{get_formatted_crossref_reference(cif_ranks[i]['doi'])[0].encode('cp850','replace').decode('cp850')}\n"
    with open(output_path / 'rank_WindowsNotepad.txt', 'w') as output_file:
        output_file.write(rank_doi_score_txt_write)
    with open(output_path / 'rank_PyCharm_Notepad++.txt', 'w') as output_file:
        output_file.write(rank_doi_score_txt_print)

    return rank_doi_score_txt_print


def terminal_print(rank_doi_score_txt):
    '''
    given an iterable object, the object is printed to the terminal, encapsulated by 80 dashes before and after.
    
    Parameters
    ----------
    iterable_object  iterable object
      e.g. a list of strings

    Returns
    -------
    None
    '''
    print('-' * 81)
    for e in rank_doi_score_txt:
        print(e)
    print('-' * 81)

    return None
