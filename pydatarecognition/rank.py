import os
from pathlib import Path
import psutil
import tempfile
import uuid
import asyncio
from asyncio import BoundedSemaphore
from typing import Optional, Literal

from motor.motor_asyncio import AsyncIOMotorClient

import numpy as np

from skbeam.core.utils import twotheta_to_q

import scipy

from pydatarecognition.cif_io import user_input_read
from pydatarecognition.powdercif import PydanticPowderCif
from pydatarecognition.utils import xy_resample
from pydatarecognition.plotters import rank_plot

filepath = Path(os.path.abspath(__file__))

STEPSIZE_REGULAR_QGRID = 10**-3

COLLECTION = "cif"
MAX_MONGO_FIND = 1000000


# Create an app level semaphore to prevent overloading the RAM. Assume ~100KB per cif, *5000 = 0.5GB
semaphore = BoundedSemaphore(5000)


async def rank_db_cifs(db: AsyncIOMotorClient, xtype: Literal["twotheta", "q"], wavelength: float,
                       user_input: bytes, filter_key: Optional[str] = None, filter_value: Optional[str] = None,
                       plot: bool = False):
    cifname_ranks = []
    r_pearson_ranks = []
    doi_ranks = []
    cif_dict = {}
    tempdir = tempfile.gettempdir()
    file_name = f'temp_{uuid.uuid4()}.txt'
    temp_filepath = os.path.join(tempdir, file_name)
    with open(temp_filepath, 'wb') as w:
        w.write(user_input)
    userdata = user_input_read(temp_filepath)
    user_x_data, user_intensity = userdata[0, :], userdata[1:, ][0]
    if xtype == 'twotheta':
        user_q = twotheta_to_q(np.radians(user_x_data), wavelength)
    else:
        user_q = user_x_data
    if filter_key is not None and filter_value is not None:
        cif_cursor = db[COLLECTION].find({filter_key: filter_value})
    else:
        cif_cursor = db[COLLECTION].find({})
    mem_premongo = psutil.virtual_memory().percent
    unpopulated_cif_list = await cif_cursor.to_list(length=MAX_MONGO_FIND)
    mem_postmongo = psutil.virtual_memory().percent
    print(f"Memory mongo_used in percent: {(mem_postmongo - mem_premongo)}")
    futures = [limited_cif_load(cif) for cif in unpopulated_cif_list]
    for future in asyncio.as_completed(futures):
        mongo_cif = await future
        try:
            data_resampled = xy_resample(user_q, user_intensity, mongo_cif.q, mongo_cif.intensity, STEPSIZE_REGULAR_QGRID)
            pearson = scipy.stats.pearsonr(data_resampled[0][:, 1], data_resampled[1][:, 1])
            r_pearson = pearson[0]
            if plot:
                p_pearson = pearson[1]
            cifname_ranks.append(mongo_cif.cif_file_name)
            r_pearson_ranks.append(r_pearson)
            doi = get_iucr_doi(mongo_cif.iucrid)
            doi_ranks.append(doi)
            if plot:
                cif_dict[str(mongo_cif.cif_file_name)] = dict([
                    ('intensity', mongo_cif.intensity),
                    ('q', mongo_cif.q),
                    ('qmin', np.amin(mongo_cif.q)),
                    ('qmax', np.amax(mongo_cif.q)),
                    ('q_reg', data_resampled[1][:, 0]),
                    ('intensity_resampled', data_resampled[1][:, 1]),
                    ('r_pearson', r_pearson),
                    ('p_pearson', p_pearson),
                    ('doi', doi),
                ])
        except AttributeError:
            print(f"{mongo_cif.cif_file_name} was skipped.")
        loop_mem = psutil.virtual_memory().percent
        print(f"Memory Used in loop in percent: {(loop_mem - mem_postmongo)}")
        semaphore.release()

    cif_rank_pearson = sorted(list(zip(cifname_ranks, r_pearson_ranks, doi_ranks)), key=lambda x: x[1], reverse=True)
    ranks = [{'IUCrCIF': cif_rank_pearson[i][0],
              'score': cif_rank_pearson[i][1],
              'doi': cif_rank_pearson[i][2]} for i in range(len(cif_rank_pearson))]
    os.remove(temp_filepath)
    if plot:
        output_plot = rank_plot(data_resampled[0][:, 0], data_resampled[0][:, 1], cif_rank_pearson, cif_dict)
        return ranks, output_plot
    else:
        return ranks


async def limited_cif_load(cif: dict):
    await semaphore.acquire()
    pcd = PydanticPowderCif(**cif)
    await pcd.resolve_gcs_tokens()
    return pcd
