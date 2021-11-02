import os
from pathlib import Path

from fastapi import APIRouter, Body, HTTPException, status, File, Depends
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from starlette.requests import Request

from typing import List, Optional, Literal

from pydatarecognition.powdercif import PydanticPowderCif
from pydatarecognition.dependencies import get_user
from pydatarecognition.mongo_client import mongo_client
from pydatarecognition.rank import rank_db_cifs

import numpy as np

filepath = Path(os.path.abspath(__file__))

STEPSIZE_REGULAR_QGRID = 10**-3

COLLECTION = "cif"
MAX_MONGO_FIND = 1000000


# Setup cif mapping reference
CIF_DIR = filepath.parent.parent / 'docs' / 'examples' / 'cifs'
doifile = CIF_DIR / 'iucrid_doi_mapping.txt'
dois = np.genfromtxt(doifile, dtype='str')
doi_dict = {}
for i in range(len(dois)):
    doi_dict[dois[i][0]] = dois[i][1]


router = APIRouter(
    prefix="/API",
    dependencies=[Depends(get_user)],
    responses={404: {"description": "Not found"}},
)


@router.route('/openapi.json')
async def get_open_api_endpoint(request: Request):  # This dependency protects our endpoint!
    response = JSONResponse(get_openapi(title='FastAPI', version=1, routes=router.routes))
    return response


@router.get(
    "/{id}", response_description="Get a single CIF", response_model=PydanticPowderCif
)
async def show_cif(id: str):
    db_client = await mongo_client.get_db_client()
    db = db_client.test
    if (cif := await db[COLLECTION].find_one({"_id": id})) is not None:
        return cif

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@router.put("/{id}", response_description="Update a CIF", response_model=PydanticPowderCif)
async def update_cif(id: str, cif: PydanticPowderCif = Body(...)):
    db_client = await mongo_client.get_db_client()
    db = db_client.test
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
    db_client = await mongo_client.get_db_client()
    db = db_client.test
    delete_result = await db[COLLECTION].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@router.get(
    "/MQL/{filter_key}/{filter_criteria}", response_description="List filtered cifs", response_model=List[PydanticPowderCif]
)
async def list_cifs(filter_key: str, filter_criteria: str):
    db_client = await mongo_client.get_db_client()
    db = db_client.test
    cifs = await db[COLLECTION].find({filter_key: filter_criteria}).to_list()
    return cifs


@router.put(
    "/rank/", response_description="Rank matches to User Input Data", tags=['rank']
)
async def rank_cif(xtype: Literal["twotheta", "q"], wavelength: float, user_input: bytes = File(...), paper_filter_iucrid: Optional[str] = None):
    db_client = await mongo_client.get_db_client()
    db = db_client.test
    return await rank_db_cifs(db, xtype, wavelength, user_input, "iucrid", paper_filter_iucrid, plot=False)
