import os
import sys
import numpy as np
import CifFile
from diffpy.structure.parsers.p_cif import _fixIfWindowsPath
from diffpy.utils.parsers.loaddata import loadData
from pydatarecognition.powdercif import PydanticPowderCif, PowderCif
from pydatarecognition.utils import get_formatted_crossref_reference
import json

DEG = "deg"


def cif_read(cif_file_path, verbose=None):
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
    if not verbose:
        verbose = False
    outputdir = cif_file_path.parent.parent / "_output"
    if not outputdir.exists():
        outputdir.mkdir()
    cache = cif_file_path.parent / "_cache"
    if not cache.exists():
        cache.mkdir()
        with open(outputdir / "no_twotheta.txt", mode="w") as o:
            o.write('')
        with open(outputdir / "no_intensity.txt", mode="w") as o:
            o.write('')
        with open(outputdir / "no_wavelength.txt", mode="w") as o:
            o.write('')
    acache = cache / f"{cif_file_path.stem}.npy"
    mcache = cache / f"{cif_file_path.stem}.json"
    cachegen = cache.glob("*.npy")
    index = list(set([file.stem for file in cachegen]))
    no_twotheta, no_intensity, no_wavelength = '', '', ''
    if cif_file_path.stem in index:
        if verbose:
            print("Getting from Cache")
        qi = np.load(acache, allow_pickle=True)
        q = qi[0]
        intensity = qi[1]
        po = PydanticPowderCif.parse_file(mcache)
        po.q, po.intensity, po.cif_file_name = q, intensity, cif_file_path.stem
    else:
        if verbose:
            print("Getting from Cif File")
        cifdata = CifFile.ReadCif(_fixIfWindowsPath(str(cif_file_path)))
        cifdata_keys = cifdata.keys()
        twotheta_keys = ['_pd_meas_2theta_corrected',
                         '_pd_proc_2theta_corrected',
                         '_pd_meas_2theta_scan',
                         '_pd_meas_2theta_range',
                         '_pd_proc_2theta_range_',
                         '_pd_meas_counts_total'
                         ]
        twotheta_range_keys = ['_pd_meas_2theta_range_min',
                               '_pd_meas_2theta_range_max']
        intensity_keys = ['_pd_meas_intensity_total',
                          '_pd_meas_intensity_net',
                          '_pd_meas_intensity_total_su',
                          '_pd_proc_intensity_total',
                          '_pd_proc_intensity_net',
                          '_pd_proc_intensity_total_su',
                          '_pd_proc_intensity_net_su',
                          '_pd_proc_intensity_bkg_calc',
                          '_pd_proc_intensity_bkg_fix',
                          '_pd_calc_intensity_total',
                          '_pd_calc_intensity_net',
                          ]
        cif_twotheta, cif_intensity = None, None
        for k in cifdata_keys:
            for ttkey in twotheta_keys:
                try:
                    cif_twotheta = np.char.split(cifdata[k][ttkey], '(')
                    cif_twotheta = np.array([float(e[0]) for e in cif_twotheta])
                except KeyError:
                    pass
                if not isinstance(cif_twotheta, type(None)):
                    break
            for intkey in intensity_keys:
                try:
                    cif_intensity = np.char.split(cifdata[k][intkey], '(')
                    if not isinstance(cif_twotheta, type(None)) and not isinstance(cif_intensity, type(None)):
                        if len(cif_intensity) != len(cif_twotheta):
                            # FIXME Handle instances multiple blocks with twotheta and intensity keys (eg. br6178Isup3.rtv.combined)
                            # cif_intensity = None
                            pass
                    try:
                        cif_intensity = np.array([float(e[0]) for e in cif_intensity])
                    except (ValueError, TypeError):
                        # FIXME Handle instances of "." for intensity values. (e.g. av5088sup2.rtv.combined)
                        # FIXME seems to be handled below within this function, i.e. twotheta and intensity arrays
                        # FIXME come out with the same length. However, powdercif.py turns intensity array into len of 0.
                        # cif_intensity = None
                        pass
                    #     cif_intensity_dots = [i for i in range(len(cif_intensity)) if cif_intensity[i][0] == "."]
                    #     cif_intensity = np.delete(cif_intensity, cif_intensity_dots)
                    #     cif_twotheta = np.delete(cif_twotheta, cif_intensity_dots)
                    #     break
                except KeyError:
                    pass
                if not isinstance(cif_intensity, type(None)):
                    break
            if isinstance(cif_twotheta, type(None)) and not isinstance(cif_intensity, type(None)):
                try:
                    twotheta_range_min = float(cifdata[k]['_pd_meas_2theta_range_min'].split("(")[0])
                    twotheta_range_max = float(cifdata[k]['_pd_meas_2theta_range_max'].split("(")[0])
                    cif_twotheta = np.linspace(twotheta_range_min, twotheta_range_max, len(cif_intensity),
                                               endpoint=True)
                except KeyError:
                    pass
        if isinstance(cif_twotheta, type(None)):
            no_twotheta += f"{cif_file_path.name}\n"
        if isinstance(cif_intensity, type(None)):
            no_intensity += f"{cif_file_path.name}\n"
        for key in cifdata_keys:
            wavelength_kwargs = {}
            #ZT Question: why isn't this _pd_proc_wavelength rather than _diffrn_radiation_wavelength?
            cif_wavelength = cifdata[key].get('_diffrn_radiation_wavelength')
            if isinstance(cif_wavelength, list):
                # FIXME Problem when wavelength is stated as an interval. (eg. '1.24-5.36' in fa3079Isup2.rtv.combined)
                try:
                    wavelength_kwargs['wavelength'] = float(cif_wavelength[0].split("(")[0]) # FIXME Handle lists
                    wavelength_kwargs['wavel_units'] = "ang"
                    break # FIXME Don't just go with first instance of wavelength.
                except ValueError:
                    wavelength_kwargs['wavelength'] = None
                    break
            elif isinstance(cif_wavelength, str):
                # FIXME Problem when wavelength is stated as an interval. (eg. '1.24-5.36' in fa3079Isup2.rtv.combined)
                try:
                    wavelength_kwargs['wavelength'] = float(cif_wavelength.split("(")[0])
                    wavelength_kwargs['wavel_units'] = "ang"
                    break
                except ValueError:
                    wavelength_kwargs['wavelength'] = None
                    break # FIXME Don't just go with first instance of wavelength.
            else:
                pass
        if not cif_wavelength:
            wavelength_kwargs['wavelength'] = None
            no_wavelength += f"{cif_file_path.name}\n"
        po = PydanticPowderCif(cif_file_path.stem[0:6],
                       DEG, cif_twotheta, cif_intensity, cif_file_path=cif_file_path.stem,
                       **wavelength_kwargs
                       )
        with open(outputdir / "no_twotheta.txt", mode="a") as o:
            o.write(no_twotheta)
        with open(outputdir / "no_intensity.txt", mode="a") as o:
            o.write(no_intensity)
        with open(outputdir / "no_wavelength.txt", mode="a") as o:
            o.write(no_wavelength)
    #TODO serialize all as json rather than npy save and see if how the cache speed compares
    with open(acache, "wb") as o:
        np.save(o, np.array([po.q, po.intensity]))
    with open(mcache, "w") as o:
        o.write(po.json(include={'iucrid', 'wavelength', 'id'}))

    return po


def cif_read_ext(cif_file_path, client):
    if not client:
        client = "fs"
    if client == "fs":
        return cif_read(cif_file_path)
    if client == "json":
        po = cif_read(cif_file_path)
        return powdercif_to_json(po)

    return None


def powdercif_to_json(po):
    json_object = {}
    if hasattr(po, 'iucrid'):
        json_object['iucrid'] = po.iucrid
    if hasattr(po, 'wavelength'):
        json_object['wavelength'] = po.wavelength
    if hasattr(po, 'ttheta'):
        json_object['ttheta'] = getattr(po.ttheta, 'tolist()', [])
    if hasattr(po, 'q'):
        json_object['q'] = getattr(po.q, 'tolist()', [])
    if hasattr(po, 'intensity'):
        json_object['intensity'] = getattr(po.intensity, 'tolist()', [])

    return json_object

def json_dump(json_object, output_path):
    with open(output_path, 'w') as f:
        json.dump(json_object, f)

    return


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


def rank_write(cif_ranks, output_path, ranktype):
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
    tab_char = '\t'
    rank_doi_score_txt_print = f"Rank\tScore\tDOI{tab_char*7}Reference\n"
    rank_doi_score_txt_write = f"Rank\tScore\tDOI{tab_char*7}Reference\n"
    for i in range(len(cif_ranks)):
        # ref_string, _ = get_formatted_crossref_reference(cif_ranks[i]['doi'])
        # encoded_ref_string = ref_string.encode('cp850', 'replace').decode('cp850')
        rank_doi_score_txt_write += f"{i+1}\t{cif_ranks[i]['score']:.4f}\t{cif_ranks[i]['doi']}\t" \
                                    f"{cif_ranks[i]['ref']}\n"
        rank_doi_score_txt_print += f"{i+1}{tab_char*2}{cif_ranks[i]['score']:.4f}\t{cif_ranks[i]['doi']}\t" \
                                    f"{cif_ranks[i]['ref']}\n"
    with open(output_path / f'rank_WindowsNotepad_{ranktype}.txt', 'w', encoding="utf-8") as output_file:
        output_file.write(rank_doi_score_txt_write)
    with open(output_path / f'rank_PyCharm_Notepad++_{ranktype}.txt', 'w', encoding="utf-8") as output_file:
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


if __name__=="__main__":
    import pathlib
    toubling_path = pathlib.Path(os.path.join(os.pardir, 'docs\\examples\\cifs\\kd5015Mg3OH5Cl-4H20sup2.rtv.combined.cif'))
    po = cif_read(toubling_path)
    po.q
