import sys
import numpy as np
import scipy.stats
from scipy.interpolate import interp1d
from urllib.request import urlopen
from requests import HTTPError
from habanero import Crossref
from datetime import date


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
    xy1_reg, xy2_reg = np.column_stack((x_reg, xy1_interpol(x_reg))), np.column_stack((x_reg, xy2_interpol(x_reg)))

    return xy1_reg, xy2_reg


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


def round_number_esd(number, esd):
    '''
    Rounds each element in number and each element in esd (estimated standard deviation) arrays.

    Esd is rounded to one significant figure if esd > 1.44E**x.(NB: 1.45E**x will become 2E**x)
    If esd <= 1.44E**x the esd is rounded to two significant figures.
    Number is rounded to the order of the rounded esd.

    Parameters
    ----------
    number : array-like
        The array containing numbers to be rounded.
    esd : array-like
        The array containing esds to be rounded.

    Returns
    -------
    list
        The list containing rounded numbers as floats and/or integers.
    list
        The list containing rounded esds as floats and/or integers.

    '''
    # Empty lists to append to.
    number_rounded, esd_rounded = [], []

    # Loop through all elements in number (and esd) arrays.
    for i in range(len(number)):

        # Getting the value and value error to be rounded.
        val, val_err = number[i], esd[i]

        # Turn val_err into scientific notation.
        val_err_sci = f"{val_err:.5E}"

        # If val < val_err than set the value to 0 and the significant figures to 1.
        if val < val_err:
            val, sig_figs = 0, 1

        # Inspect first significant figure of val_err_sci.
        # If the first significant figure is 1, we need to inspect the next.
        # Else, we can set the number of significant figures to 1.
        elif int(val_err_sci[0]) == 1:
            # Inspect the second significant figure.
            # Take care of cases where we always want 2 significant figures:
            # val_err < 1.4E**x
            if int(val_err_sci[2]) < 4:
                sig_figs = 2

            # Inspect the edge case of the second significant figure.
            # Make sure that we round up, if val_err >= 1.45E**x,
            # and set the number of significant figures to 1.
            # Else round down (that is, if val_err < 1.45E**x).
            # and the set number of significant figures to 2.
            elif int(val_err_sci[2]) == 4:
                if int(val_err_sci[3]) >= 5:
                    val_err_sci = f"{val_err_sci[0:2]}5{val_err_sci[3::]}"
                    val_err = float(val_err_sci)
                    sig_figs = 1
                else:
                    sig_figs = 2
            else:
                sig_figs = 1
        else:
            sig_figs = 1

        # Get the order of magnitude of the val_err.
        n = int(np.log10(val_err))

        # Take into account if we need to 'correct' the order of magnitude.
        # Related to the 'scale' below.
        if val_err >= 1:
            n += 1

        # Set the scale, considering number of significant figures,
        # and the order of magnitude.
        scale = 10 ** (sig_figs - n)

        # Use floor rounding. Add 0.5 to make sure that we round up for halfs.
        # (However, remember that np.floor always rounds down...)
        val = np.floor(val * scale + 0.5) / scale
        val_err = np.floor(val_err * scale + 0.5) / scale

        # Take into account, if the val_err >= 1.
        # Then, we get rid of any decimals.
        if val_err >= 1:
            val, val_err = int(val), int(val_err)

        # Append to rounded number and esd to lists.
        number_rounded.append(val)
        esd_rounded.append(val_err)

    return number_rounded, esd_rounded


def hr_to_mr_number_and_esd(number_esd):
    '''
    splits human readable numbers with estimated standard deviations (e.g. 343.44(45)) into rounded machine readable
    numbers and estimated standard deviations (e.g. 343.4 and 0.5).

    Parameters
    ----------
    number_esd : array_like
      The array-like object that contains numbers with their estimated standard deviations as strings
      in the following format: ["343.44(45)", "324908.435(67)", "0.0783(1)"]

    Returns
    -------
    list
      The list with the rounded numbers as floats, e.g. [343.4, 324908.44, 0.0783]

    list
      The list with rounded estimated standard deviations as floats, e.g. [0.5, 0.07, 0.0001]

    '''
    number = [e.split("(")[0] for e in number_esd]
    esd = [e.split("(")[1].split(")")[0] for e in number_esd]
    esd_oom = []
    for i in range(len(number)):
        if len(number[i].split(".")) == 1:
            esd_oom.append(1)
        else:
            esd_oom.append(10**-len(number[i].split(".")[1]))
    esd_oom = np.array(esd_oom, dtype='float')
    esd = list(np.array(esd, dtype='float') * np.array(esd_oom, dtype='float'))
    number_floats = [float(e) for e in number]
    number_rounded, esd_rounded = round_number_esd(number_floats, esd)

    return number_rounded, esd_rounded


def mr_to_hr_number_and_esd(number, esd):
    '''
    rounds and merges machine readable numbers and estimated standard deviations (e.g. 343.4 and 0.5)
    into human readable numbers with estimated standard deviations (e.g. 343.4(5)).

    Parameters
    ----------
    number : array-like
        The array that contains numbers.
    esd : array-like
        The array that contains esds.

    Returns
    -------
    list
        The list of strings with human readable rounded numbers and esds.

    '''
    number_rounded, esd_rounded = round_number_esd(number, esd)
    esd_hr = []
    for e in esd_rounded:
        if e < 1:
            esd_hr.append(int(str(e).split(".")[1]))
        else:
            esd_hr.append(e)
    number_esd = [f"{number_rounded[i]}({esd_hr[i]})" for i in range(len(number_rounded))]

    return number_esd

  
  def correlate(y1, y2, corr_type='pearson'):
    '''
    
    Parameters
    ----------
    y1 : array-like
        The first array that we want to include in the correlation analysis. 
    y2 : array-like
        The second array that we want to include in the correlation analysis.
    corr_type : str
        The string that indicates which type of correlation analysis that we want to conduct for arrays y1 and y2.
        The allowed types are 'pearson', 'spearman', 'kendall'.

    Returns
    -------
    float
        The correlation coefficient obtained from the correlation analysis.
    '''
    corr_types = ['pearson', 'spearman', 'kendall']
    if not corr_type.lower() in corr_types:
        print(f"The corr_type provided is not valid.\
                \nValid corr_types are {corr_types}.\
                \nBy default, the corr_type has been set to 'pearson'.\
                \nIf some other corr_type is desired, please rerun with valid corr_type.")
        corr_coeff, pvalue = scipy.stats.pearsonr(np.array(y1), np.array(y2))
    if corr_type.lower() == 'spearman':
        corr_coeff, pvalue = scipy.stats.spearmanr(np.array(y1), np.array(y2))
    elif corr_type.lower() == 'kendall':
        corr_coeff, pvalue = scipy.stats.kendalltau(np.array(y1), np.array(y2))
    elif corr_type.lower() == 'pearson':
        corr_coeff, pvalue = scipy.stats.pearsonr(np.array(y1), np.array(y2))
    if np.isnan(corr_coeff):
        raise ValueError('nan obtained corr_coeff.')

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


# End of file.
