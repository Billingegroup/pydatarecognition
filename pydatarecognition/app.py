import os
from pathlib import Path
import yaml
import tempfile
import shutil
import uuid

from fastapi import FastAPI, Body, HTTPException, status, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional, Literal
import motor.motor_asyncio
from pydatarecognition.powdercif import PydanticPowderCif
from pydatarecognition.utils import xy_resample
from pydatarecognition.cif_io import user_input_read
from skbeam.core.utils import twotheta_to_q
import scipy.stats
import numpy as np

STEPSIZE_REGULAR_QGRID = 10**-3

COLLECTION = "cif"

<<<<<<< Updated upstream
app = FastAPI()

# Connect to mongodb
filepath = Path(os.path.abspath(__file__))
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
=======
app = FastAPI(docs_url=None, redoc_url=None)
app.add_event_handler("startup", mongo_client.connect_db)
app.add_event_handler("shutdown", mongo_client.close_mongo_connection)
app.include_router(rest_api.router)
app.mount("/static", StaticFiles(directory="pydatarecognition/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key='!secret')
templates = Jinja2Templates(directory="pydatarecognition/templates")
>>>>>>> Stashed changes




@app.post("/", response_description="Add new CIF", response_model=PydanticPowderCif)
async def create_cif(powdercif: PydanticPowderCif = Body(...)):
    powdercif = jsonable_encoder(powdercif)
    new_cif = await db[COLLECTION].insert_one(powdercif)
    created_cif = await db[COLLECTION].find_one({"_id": new_cif.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_cif)


@app.get(
    "/", response_description="List all cifs", response_model=List[PydanticPowderCif]
)
async def list_cifs():
    cifs = await db[COLLECTION].find().to_list(5)
    return cifs


@app.get(
    "/{id}", response_description="Get a single CIF", response_model=PydanticPowderCif
)
async def show_cif(id: str):
    if (cif := await db[COLLECTION].find_one({"_id": id})) is not None:
        return cif

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@app.put("/{id}", response_description="Update a CIF", response_model=PydanticPowderCif)
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


@app.delete("/{id}", response_description="Delete a CIF")
async def delete_cif(id: str):
    delete_result = await db[COLLECTION].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")

@app.put(
    "/query/", response_description="Rank matches to User Input Data"
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
    if paper_filter_iucrid:
        cif_list = db[COLLECTION].find({"iucrid": paper_filter_iucrid})
    else:
        cif_list = db[COLLECTION].find({})
    async for cif in cif_list:
        mongo_cif = PydanticPowderCif(**cif)
        try:
            data_resampled = xy_resample(user_q, user_q, mongo_cif.q, mongo_cif.intensity, STEPSIZE_REGULAR_QGRID)
            pearson = scipy.stats.pearsonr(data_resampled[0][:, 1], data_resampled[1][:, 1])
            r_pearson = pearson[0]
            p_pearson = pearson[1]
            cifname_ranks.append(mongo_cif.cif_file_name)
            r_pearson_ranks.append(r_pearson)
            doi = doi_dict[mongo_cif.iucrid]
            doi_ranks.append(doi)
        except AttributeError:
            print(f"{mongo_cif.cif_file_name} was skipped.")

    cif_rank_pearson = sorted(list(zip(cifname_ranks, r_pearson_ranks, doi_ranks)), key=lambda x: x[1], reverse=True)
    ranks = [{'IUCrCIF': cif_rank_pearson[i][0],
              'score': cif_rank_pearson[i][1],
              'doi': cif_rank_pearson[i][2]} for i in range(len(cif_rank_pearson))]
    shutil.rmtree(tempdir)
    return ranks


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
