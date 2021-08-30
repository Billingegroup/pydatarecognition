import os
from pathlib import Path
import yaml
import tempfile
import shutil
import uuid
import asyncio
from asyncio import BoundedSemaphore

from fastapi import APIRouter, Body, HTTPException, status, File, Depends
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from starlette.requests import Request

from typing import List, Optional, Literal

import motor.motor_asyncio

from pydatarecognition.powdercif import PydanticPowderCif
from pydatarecognition.utils import xy_resample
from pydatarecognition.cif_io import user_input_read
from pydatarecognition.dependencies import get_user

from skbeam.core.utils import twotheta_to_q

import scipy.stats

import numpy as np

import psutil

filepath = Path(os.path.abspath(__file__))

STEPSIZE_REGULAR_QGRID = 10**-3

COLLECTION = "cif"
MAX_MONGO_FIND = 1000000

# Connect to mongodb

with open(os.path.join(filepath.parent, 'secret_password.yml'), 'r') as f:
    user_secrets = yaml.safe_load(f)
username = user_secrets['username']
password = user_secrets['password']
client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb+srv://{username}:{password}@sidewinder.uc5ro.mongodb.net/?retryWrites=true&w=majority')
db = client.test

# Setup cif mapping reference
CIF_DIR = filepath.parent.parent / 'docs' / 'examples' / 'cifs'
doifile = CIF_DIR / 'iucrid_doi_mapping.txt'
dois = np.genfromtxt(doifile, dtype='str')
doi_dict = {}
for i in range(len(dois)):
    doi_dict[dois[i][0]] = dois[i][1]


# Create an app level semaphore to prevent overloading the RAM. Assume ~100KB per cif, *5000 = 0.5GB
semaphore = BoundedSemaphore(5000)


router = APIRouter(
    prefix="/API",
    dependencies=[Depends(get_user)],
    responses={404: {"description": "Not found"}},
)


@router.get('/docs', tags=['documentation'])  # Tag it as "documentation" for our docs
async def get_documentation(request: Request):  # This dependency protects our endpoint!
    response = get_swagger_ui_html(openapi_url='/openapi.json', title='Documentation')
    return response


@router.route('/openapi.json')
async def get_open_api_endpoint(request: Request):  # This dependency protects our endpoint!
    response = JSONResponse(get_openapi(title='FastAPI', version=1, routes=router.routes))
    return response


@router.get(
    "/{id}", response_description="Get a single CIF", response_model=PydanticPowderCif
)
async def show_cif(id: str):
    if (cif := await db[COLLECTION].find_one({"_id": id})) is not None:
        return cif

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@router.put("/{id}", response_description="Update a CIF", response_model=PydanticPowderCif)
async def update_cif(id: str, cif: PydanticPowderCif = Body(...)):
    cif = {k: v for k, v in cif.dict().items() if v is not None}

    if len(cif) >= 1:
        update_result = await db[COLLECTION].update_one({"_id": id}, {"$set": cif})

        if update_result.modified_count == 1:
            if (
                updated_cif := await db[COLLECTION].find_one({"_id": id})
            ) is not None:
                return updated_cif

    if (existing_cif := await db[COLLECTION].find_one({"_id": id})) is not None:
        return existing_cif

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@router.delete("/{id}", response_description="Delete a CIF")
async def delete_cif(id: str):
    delete_result = await db[COLLECTION].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@router.get(
    "/{filter_key}/{filter_criteria}", response_description="List filtered cifs", response_model=List[PydanticPowderCif]
)
async def list_cifs(filter_key: str, filter_criteria: str):
    cifs = await db[COLLECTION].find({filter_key: filter_criteria}).to_list()
    return cifs


@router.put(
    "/rank/", response_description="Rank matches to User Input Data", tags=['rank']
)
async def rank_cif(xtype: Literal["twotheta", "q"], wavelength: float, user_input: bytes = File(...), paper_filter_iucrid: Optional[str] = None):
    cifname_ranks = []
    r_pearson_ranks = []
    doi_ranks = []
    tempdir = tempfile.mkdtemp()
    temp_filename = os.path.join(tempdir, f'temp_{uuid.uuid4()}.txt')
    with open(temp_filename, 'wb') as w:
        w.write(user_input)
    userdata = user_input_read(temp_filename)
    user_x_data, user_intensity = userdata[0, :], userdata[1:, ][0]
    if xtype == 'twotheta':
        user_q = twotheta_to_q(np.radians(user_x_data), wavelength)
    else:
        user_q = user_x_data
    if paper_filter_iucrid:
        cif_cursor = db[COLLECTION].find({"iucrid": paper_filter_iucrid})
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
            cifname_ranks.append(mongo_cif.cif_file_name)
            r_pearson_ranks.append(r_pearson)
            doi = doi_dict[mongo_cif.iucrid]
            doi_ranks.append(doi)
        except AttributeError:
            print(f"{mongo_cif.cif_file_name} was skipped.")
        loop_mem = psutil.virtual_memory().percent
        print(f"Memory Used in loop in percent: {(loop_mem - mem_postmongo)}")
        semaphore.release()

    cif_rank_pearson = sorted(list(zip(cifname_ranks, r_pearson_ranks, doi_ranks)), key=lambda x: x[1], reverse=True)
    ranks = [{'IUCrCIF': cif_rank_pearson[i][0],
              'score': cif_rank_pearson[i][1],
              'doi': cif_rank_pearson[i][2]} for i in range(len(cif_rank_pearson))]
    shutil.rmtree(tempdir)
    return ranks


async def limited_cif_load(cif: dict):
    await semaphore.acquire()
    pcd = PydanticPowderCif(**cif)
    await pcd.resolve_gcs_tokens()
    return pcd