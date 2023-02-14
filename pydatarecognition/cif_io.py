import os
import numpy as np
import CifFile
from diffpy.utils.parsers.loaddata import loadData
from pydatarecognition.powdercif import PydanticPowderCif
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
        with open(cif_file_path, "r") as fs:
            cifdata = CifFile.ReadCif(fs)
        cifdata_keys = cifdata.keys()
        twotheta_keys = ['_pd_meas_2theta_corrected',
                         '_pd_meas_2theta_scan',
                         '_pd_meas_2theta_range',
                         '_pd_proc_2theta_corrected',
                         '_pd_proc_2theta_range_',
                         ]
        twotheta_min_keys = ['_pd_meas_2theta_range_min',
                             '_pd_proc_2theta_range_min',
                             ]
        twotheta_max_keys = ['_pd_meas_2theta_range_max',
                             '_pd_proc_2theta_range_max',
                             ]
        twotheta_inc_keys = ['_pd_meas_2theta_range_inc',
                             '_pd_proc_2theta_range_inc',
                             ]
        intensity_keys = ['_pd_meas_counts_total',
                          '_pd_meas_intensity_total',
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
        cif_twotheta, cif_intensity, cif_twotheta_min, cif_twotheta_max, twotheta_inc = None, None, None, None, None
        for k in cifdata_keys:
            for ttkey in twotheta_keys:
                try:
                    cif_twotheta = np.char.split(cifdata[k][ttkey], '(')
                    cif_twotheta = np.array([float(e[0]) for e in cif_twotheta])
                except KeyError:
                    pass
                if cif_twotheta is not None:
                    break
            for intkey in intensity_keys:
                try:
                    cif_intensity = np.char.split(cifdata[k][intkey], '(')
                    cif_intensity = np.array([e[0] for e in cif_intensity])
                    for e in [',', '.', '?', '-']:
                        while cif_intensity[-1] == e:
                            cif_intensity = np.delete(cif_intensity, -1)
                            if cif_twotheta is not None:
                                cif_twotheta = np.delete(cif_twotheta, -1)
                    for i in range(len(cif_intensity)-1, -1, -1):
                        for e in [',', '.', '?', '-']:
                            if cif_intensity[i] == e:
                                cif_intensity = np.delete(cif_intensity, i)
                                if cif_twotheta is not None:
                                    cif_twotheta = np.delete(cif_twotheta, i)
                except KeyError:
                    pass
                if not isinstance(cif_intensity, type(None)):
                    break
        if isinstance(cif_twotheta, type(None)) and not isinstance(cif_intensity, type(None)):
            for k in cifdata_keys:
                for ttminkey in twotheta_min_keys:
                    try:
                        cif_twotheta_min = cifdata[k][ttminkey].split("(")[0]
                        try:
                            cif_twotheta_min = float(cif_twotheta_min)
                            break
                        except ValueError:
                            cif_twotheta_min = None
                            pass
                    except KeyError:
                        pass
                for ttmaxkey in twotheta_max_keys:
                    try:
                        cif_twotheta_max = cifdata[k][ttmaxkey].split("(")[0]
                        try:
                            cif_twotheta_max = float(cif_twotheta_max)
                            break
                        except ValueError:
                            cif_twotheta_max = None
                            pass
                    except KeyError:
                        pass
                for ttinckey in twotheta_inc_keys:
                    try:
                        cif_twotheta_inc = cifdata[k][ttinckey].split("(")[0]
                        try:
                            cif_twotheta_inc = float(cif_twotheta_inc)
                            break
                        except ValueError:
                            cif_twotheta_inc = None
                            pass
                    except KeyError:
                        pass
                # if not isinstance(cif_twotheta_min, type(None)) and not isinstance(cif_twotheta_max, type(None)):
                    # print(f"{cif_file_path.name}".upper())
                    # cif_twotheta = np.linspace(cif_twotheta_min, cif_twotheta_max, len(cif_intensity),
                    #                            endpoint=True)
                if cif_twotheta_min and cif_twotheta_max and cif_twotheta_inc:
                    cif_twotheta = np.arange(cif_twotheta_min, cif_twotheta_max, cif_twotheta_inc)
                    if len(cif_intensity) - len(cif_twotheta) == 0:
                        pass
                    elif len(cif_intensity) - len(cif_twotheta) == 1:
                        cif_intensity = cif_intensity[0:-1]
                    elif len(cif_intensity) - len(cif_twotheta) == 2:
                        cif_intensity = cif_intensity[1:-1]
                    else:
                        cif_twotheta = None
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


def set_client(mpc_client='fs') -> str | None:
    """
    returns not implemented warning if mpc_client is 'mpc' and None if mpc_client if 'fs'

    Parameters
    ----------
    mpc_client  str object 'mpc (mpcontribs)' or 'fs (filesystem)'
                set 'fs' by default

    Returns
    -------
    str: 'This feature is not yet implemented' if mpc_client='mpc'
    None if mpc_client='fs'
    """
    if mpc_client == 'mpc':
        return 'This function is not yet implemented'
    elif mpc_client == 'fs':
        return None
    else:
        return 'mpc_client must be either mpc or fs'


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
      ndarray with the columns of the user input file. Dimensions will depend on the number of columns.
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

def print_story(user_input, args, ciffiles, skipped_cifs):
    frame_dashchars = '-'*80
    print(f'{frame_dashchars}\nInput data file: {user_input.name}\n'
          f"Wavelength: {args['wavelength']} Å.")
    print(f'{frame_dashchars}\nWorking with CIFs...')
    for cif in ciffiles:
        print(f"    {cif}")
    print(f'{frame_dashchars}\nSkipped CIFs...')
    for cif in skipped_cifs:
        print(f"    {cif[0]} because {cif[1]}")
    print(f'Done working with cifs.\n{frame_dashchars}\nGetting references...')

if __name__=="__main__":
    import pathlib
    toubling_path = pathlib.Path(os.path.join(os.pardir, 'docs\\examples\\cifs\\kd5015Mg3OH5Cl-4H20sup2.rtv.combined.cif'))
    po = cif_read(toubling_path)
    po.q
