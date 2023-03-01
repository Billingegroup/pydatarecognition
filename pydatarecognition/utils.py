import numpy as np
import scipy.stats
from scipy.interpolate import interp1d
from urllib.request import urlopen
from requests import HTTPError
from habanero import Crossref
from datetime import date
from skbeam.core.utils import twotheta_to_q, d_to_q


XCHOICES = ['Q', 'q', 'twotheta', 'd']
QUNITS = ["inv-A", "inv-nm"]
TTUNITS = ["deg", "rad"]
DUNITS = ["A", "nm"]
XUNITS = QUNITS + TTUNITS + DUNITS
SIMILARITY_METRICS = ['pearson', 'spearman', 'kendall']
CLIENT = ['mpc', 'fs']


NumberTypes = (int, float, complex)

def user_diffraction_data_extract(user_input_lines):
    '''
    given user_input_lines, extract twotheta values and intensity values to individual lists as floats
    Parameters
    ----------
    user_input_lines  list object
      the list containing the lines of the user input file
    Returns
    -------
    twotheta and intensity lists in a tuple
    '''
    twotheta_list, intensity_list = [], []
    for line in user_input_lines:
        twotheta_list.append(float(line.split()[0]))
        intensity_list.append(float(line.split()[1]))
    twotheta_array = np.array(twotheta_list)
    intensity_array = np.array(intensity_list)

    return twotheta_array, intensity_array


def q_calculate(twotheta_list, wavelength):
    '''
    given a list of twotheta values and wavelength, calculates and appends corresponding q values to a list
    Parameters
    ----------
    twotheta_list  list object
      the list containing the twotheta values as floats
    wavelength type string or float
      wavelength in angstroms
    Returns
    -------
    a list of q values as floats
    '''
    wavelength = float(wavelength)
    q_list = []
    for i in range(0, len(twotheta_list)):
        q_list.append(float(4 * np.pi * np.sin((np.pi / 180) * float(twotheta_list[i]) / 2) / wavelength))

    return q_list


def q_extrema_round(q_list):
    '''
    given a list of q values, gets the minimum and maximum q values
    and rounds them up and down to two significant digits, respectively
    Parameters
    ----------
    q_list  list object
      the list of q values as floats
    Returns
    -------
    the minimum q value rounded up to two significant digits as float
    the maximum q value rounded down to two significant digits as float
    '''
    q_min_round_up = float(np.ceil(min(q_list) * 10**2) / 10**2)
    q_max_round_down = float(np.floor(max(q_list) * 10**2) / 10**2)

    return q_min_round_up, q_max_round_down


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


def xy_resample(x1, y1, x2, y2, x_step=None):
    '''
    Given arrays with x and y values for two datasets, the common x-range is found. 
    A regular x-grid is calculated for this common x-range using the provided step size.
    For each of the two y arrays, linear interpolations are done.
    The interpolations are used to resample the data sets onto the regular x-grid.

    Parameters
    ----------
    x1  array_like 
      x values for data set 1.
    y1  array_like
      y values for data set 1.
    x2  array_like 
      x values for data set 2.
    y2  array_like
      y values for data set 2.      
    x_step  integer or float (non-zero and positive, optional)
      step size for regular x-grid to be calculated.
    Returns
    -------
    xy1_reg  numpy array
      data set 1 resampled onto the regular x-grid. 
    xy2_reg  numpy array
      data set 2 resampled onto the regular x-grid. 
    '''
    if not x_step:
        x_step = 10**-3
    x1, y1, x2, y2 = np.array(x1), np.array(y1), np.array(x2), np.array(y2)
    if not x2.any():
        raise AttributeError('Reciprocal space axis (3rd argument) missing (NoneType Provided)')
    xmin = max(x1[0], x2[0])
    xmax = min(x1[-1], x2[-1])
    if xmin > xmax:
        raise ValueError('Data ranges do not overlap')
    elif xmax - xmin < 20:
        raise ValueError(f'Too narrow xrange: xmax = {xmax} - xmin = {xmin} < 20')
    nox = int(((xmax - xmin) / x_step) + 1)
    x_reg = np.linspace(xmin, xmax, nox, endpoint=True)
    xy1_interpol = interp1d(x1, y1, kind='linear')
    xy2_interpol = interp1d(x2, y2, kind='linear')
    xy1_reg = np.column_stack((x_reg, xy1_interpol(x_reg)))
    xy2_reg = np.column_stack((x_reg, xy2_interpol(x_reg)))

    return xy1_reg.T, xy2_reg.T


def get_iucr_doi(iucrid):
    with urlopen(f"https://publbio.iucr.org/publcifx/cnor2doi.php?cnor={iucrid}") as url:
        doi = url.read().decode("utf-8")

    return doi


def get_formatted_crossref_reference(doi):
    '''
    given a doi, return the full reference and the date of the reference from Crossref REST-API

    parameters
    ----------
    doi str
      the doi of the digital object to pull from Crossref

    return
    ------
    ref str
      the nicely formatted reference including title
    ref_date datetime.date
      the date of the reference
    returns None None in the article cannot be found given the doi

    '''

    cr = Crossref()
    try:
        article = cr.works(ids=str(doi))
    except HTTPError:
        return None, None

    authorlist = [
        "{} {}".format(a['given'].strip(), a['family'].strip())
        for a in article.get('message').get('author')]
    try:
        journal = \
            article.get('message').get('short-container-title')[0]
    except IndexError:
        journal = article.get('message').get('container-title')[
            0]
    if article.get('message').get('volume'):
        if len(authorlist) > 1:
            authorlist[-1] = "and {}".format(authorlist[-1])
        sauthorlist = ", ".join(authorlist)
        ref_date_list = article.get('message').get('issued').get('date-parts')
        ref = "{}, {}, {}, v. {}, pp. {}, ({}).".format(
            article.get('message').get('title')[0],
            sauthorlist,
            journal,
            article.get('message').get('volume'),
            article.get('message').get('page'),
            ref_date_list[0][0],
        )
    else:
        if len(authorlist) > 1:
            authorlist[-1] = "and {}".format(authorlist[-1])
        sauthorlist = ", ".join(authorlist)
        ref_date_list = article.get('message').get('issued').get('date-parts')
        ref = "{}, {}, {}, pp.{}, ({}).".format(
            article.get('message').get('title')[0],
            sauthorlist,
            journal,
            article.get('message').get('page'),
            ref_date_list[0][0],
        )
    ref_date_list = ref_date_list[0]
    ref_date_list += [6] * (3 - len(ref_date_list))
    ref_date = date(*ref_date_list)

    return ref, ref_date


def correlate(y1, y2, correlator=None):
    f'''
    
    Parameters
    ----------
    y1 : array-like
        The first array that we want to include in the correlation analysis. 
    y2 : array-like
        The second array that we want to include in the correlation analysis.
    correlator : str
        The string that indicates which type of correlation analysis that we want to conduct for arrays y1 and y2.
        The allowed types are {*SIMILARITY_METRICS,}.

    Returns
    -------
    float
        The correlation coefficient obtained from the correlation analysis.
    '''
    if correlator is None:
        correlator = 'pearson'
    if correlator.lower() == 'pearson':
        corr_coeff, pvalue = scipy.stats.pearsonr(np.array(y1), np.array(y2))
    elif correlator.lower() == 'spearman':
        corr_coeff, pvalue = scipy.stats.spearmanr(np.array(y1), np.array(y2))
    elif correlator.lower() == 'kendall':
        corr_coeff, pvalue = scipy.stats.kendalltau(np.array(y1), np.array(y2))
    else:
        raise ValueError(f"correlator {correlator} not known.  Allowed values are {*SIMILARITY_METRICS,}")
    if np.isnan(corr_coeff):
        raise ValueError(f"similarity metric returned 'nan'")

    return float(corr_coeff)


def rank_returns(rank_dict, returns_min, returns_max, similarity_threshold):
    if rank_dict[0]['corr_coeff'] < similarity_threshold:
        returns = returns_min
    else:
        for i in range(1, len(rank_dict.keys())):
            if rank_dict[i - 1]['corr_coeff'] >= similarity_threshold > rank_dict[i]['corr_coeff']:
                returns = i
                if returns < returns_min:
                    returns = returns_min
                    break
                elif returns > returns_max:
                    returns = returns_max
                    break
                else:
                    pass

    return returns

def validate_args(args):
    if args['xquantity'] == 'twotheta' and not args['wavelength']:
        raise RuntimeError("--wavelength is required when --xquantity is twotheta. "
                           "Please rerun specifying wavelength."
                           )
    for arg in ['wavelength', 'qgrid_interval', 'similarity_threshold']:
        if args.get(arg) and not isinstance(args.get(arg), NumberTypes):
            raise RuntimeError(f"Cannot read --{arg}. Please make sure it is a number")
    if args['xquantity'] not in XCHOICES:
        raise RuntimeError(f"Cannot read --xquantity. Please provide --xquantity as one of these choices: {*XCHOICES,}")
    if args['xquantity'] == 'twotheta' and args['xunit'] not in TTUNITS:
        raise RuntimeError(f"--xquantity twotheta, allowed units are {*TTUNITS,}. Please provide --xunit with one of these choices")
    if args['xquantity'].lower() == 'q' and args['xunit'] not in QUNITS:
        raise RuntimeError(f"--xquantity Q, allowed units are {*QUNITS,}. Please provide --xunit with one of these choices")
    if args['xquantity'] == 'd' and args['xunit'] not in DUNITS:
        raise RuntimeError(f"--xquantity d-spacing, allowed units are {*DUNITS,}. Please provide --xunit with one of these choices")
    if args.get('similarity_metric') and args.get('similarity_metric') not in SIMILARITY_METRICS:
        raise RuntimeError(f"Cannot read --similarity_metric. allowed values are {*SIMILARITY_METRICS,}.")
    return True

def process_args(args):
    for arg in ['wavelength', 'qgrid_interval', 'similarity_threshold']:
        try:
            if args.get(arg):
                args[arg] = float(args[arg])
        except ValueError:
            raise ValueError(f"Cannot read --{arg.replace('_','-')}. Please make sure it is a number")
    for arg in ['returns_min_max']:
        try:
            if args.get(arg):
                args[arg] = [int(item) for item in args[arg]]
        except ValueError:
            raise ValueError(f"Cannot read --{arg.replace('_','-')}. Please make sure it is a list of numbers")
    return args

def create_q_int_arrays(args, data_array):
    '''

    Parameters
    ----------
    args
      the dictionary of command line arguments.  This contains information about
      the quantity (twotheta, q or d-spacing) and its units of the independent variable.
      It must also contain the wavelength in angstrom units.
    userdata
      the 2xN dimensional numpy arrays of the user input data which has the
      independent variable on in the first row and the intensity variable in
      the second

    Returns
    -------
    the q and intensity arrys.  the q array values are in inverse nm.

    '''
    if args.get('xquantity') == 'twotheta' and args.get('xunit') == 'deg':
        user_q = twotheta_to_q(np.radians(data_array[0]), float(args['wavelength'])/10.)
    elif args.get('xquantity') == 'twotheta' and args.get('xunit') == 'rad':
        user_q = twotheta_to_q(data_array[0], float(args.get('wavelength')) / 10.)
    elif args.get('xquantity').lower() == 'q' and args.get('xunit') == 'inv-nm':
        user_q = data_array[0]
    elif args.get('xquantity').lower() == 'q' and args.get('xunit').lower() == 'inv-a':
        user_q = data_array[0] * 10.
    elif args.get('xquantity').lower() == 'd' and args.get('xunit').lower() == 'nm':
        user_q = d_to_q(data_array[0])
    elif args.get('xquantity').lower() == 'd' and args.get('xunit').lower() == 'a':
        user_q = d_to_q(data_array[0]/10.)
    return user_q, data_array[1]

def plotting_min_max(array, whitespace_factor=None):
    if whitespace_factor is None:
        whitespace_factor = 0.1
    range = np.amax(array) - np.amin(array)
    upper = np.amax(array) + range * whitespace_factor
    lower = np.amin(array) - range * whitespace_factor
    return lower, upper

# End of file.
