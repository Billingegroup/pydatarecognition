import os
from io import BytesIO
import uuid
from pathlib import Path
# from functools import lru_cache
import re
import asyncio

import numpy as np
from skbeam.core.utils import twotheta_to_q, q_to_twotheta
from pydantic import Field, validator
from odmantic.bson import BSON_TYPES_ENCODERS, BaseBSONModel, ObjectId
from bson.errors import InvalidId
from gcloud.aio.storage import Storage
from google.cloud import storage as sync_storage

MODEL_VERSION = '0.0.1'

filepath = Path(os.path.abspath(__file__))
if os.path.isfile(os.path.join(filepath.parent.absolute(), '../requirements/testing-cif-datarec-secret.json')):
#     if os.path.isfile(os.path.join(filepath.parent.absolute(),
#                                    '../requirements/testing-cif-datarec-secret.json')):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(filepath.parent.absolute(),
                                                                '../requirements/testing-cif-datarec-secret.json')
elif os.path.isfile(os.path.join(filepath.parent.absolute(), '../requirements/production-cif-datarec-secret.json')):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(filepath.parent.absolute(),
                                                                '../requirements/production-cif-datarec-secret.json')
else:
    print('Google API credentials not found. See README.md if you intend to read/write to the external database')

BUCKET_NAME = 'raw_cif_data_simon'
DAYS_CACHED = 5
GCS_METADATA = {
                'pydantic_powder_model_version': MODEL_VERSION,
                'numpy_version': np._version.get_versions()['version'],
                'format': '.npy'
            }

try:
    # Will only work in python 3.8 and up
    from typing import Optional, Literal, get_args, Any, Union
except:
    from typing import Optional, Any, Union
    from typing_extensions import Literal, get_args

allowed_lengths = Literal["ang", "angs", "angstroms", "nm", "nanometers"]
ANGS = get_args(allowed_lengths)[0:3]
NMS = get_args(allowed_lengths)[3:5]
LENGTHS = get_args(allowed_lengths)
INVANGS = ["invang", "invangs", "inverse angstroms", "invnm", "inverse nanometers"]
allowed_x_units = Literal["invang", "invangs", "inverse angstroms", "invnm", "inverse nanometers", "deg", "degs",
                          "degrees", "rad", "rads", "radians"]
INVANGS = get_args(allowed_x_units)[0:3]
INVNMS = get_args(allowed_x_units)[3:5]
INVS = INVNMS + INVANGS
DEGS = get_args(allowed_x_units)[5:8]
RADS = get_args(allowed_x_units)[8:11]
X_UNITS = get_args(allowed_x_units)


class _ArrayMeta(type):
    def __getitem__(self, t):
        return type('Array', (Array,), {'__dtype__': t})


class Array(np.ndarray, metaclass=_ArrayMeta):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_type

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type='array',
            items={"type": "integer"}
        )

    @classmethod
    def validate_type(cls, val):
        dtype = getattr(cls, '__dtype__', Any)
        if dtype is Any:
            return np.array(val)
        else:
            return np.array(val, dtype=dtype)


async def export_to_gcs(array: np.ndarray) -> str:
    """
    Async export to gcs, can be utilized if we define a class method to export data pre-emptively
    @param array:
    @return: gcs_token
    """
    async with Storage() as storage_client:
        file_id = uuid.uuid4().hex
        out = BytesIO()
        np.save(out, array)
        out.seek(0)
        status = await storage_client.upload(BUCKET_NAME, file_id, out, metadata={
            'cache_control': f"public, max-age={int(DAYS_CACHED*60*60*24)}",
            'metadata': GCS_METADATA
        })
        print(status)
    return file_id


def json_gcs_export(array: np.ndarray) -> str:
    """
    json encoder cannot be defined with async calls, therefore the normal google cloud client is utilized
    @param array:
    @return: gcs_token
    """
    storage_client = sync_storage.Client()
    cif_bucket = storage_client.get_bucket(BUCKET_NAME)
    file_id = uuid.uuid4().hex
    blob = cif_bucket.blob(file_id)
    out = BytesIO()
    np.save(out, array)
    out.seek(0)
    blob.cache_control = f"public, max-age={int(DAYS_CACHED*60*60*24)}"
    blob.metadata = GCS_METADATA
    blob.upload_from_file(out)
    storage_client.close()
    return file_id


# Each is ~56KB, 1000 of which are 0.56GB of RAM
#TODO implement a cache when we have meaningful filerting. Normal LRu cache below will not work async
# @lru_cache(maxsize=1000, typed=True)
async def retrieve_glob_as_np(uid: str) -> np.ndarray:
    async with Storage() as storage_client:
        file = await storage_client.download(BUCKET_NAME, uid)
        buffer = BytesIO(file)
        buffer.seek(0)
    return np.load(buffer)


class PydanticPowderCif(BaseBSONModel):
    """Pydantic model of CIF Powder data for mongo database. Ingests CIF data and mongo data."""
    iucrid: Optional[str] = Field(None, description="The Unique Identifier of the Paper that is Associated With "
                                                    "the Data")
    id: Optional[ObjectId] = Field(default_factory=ObjectId, description='Mongo Identifier', alias='_id')
    cif_file_name: Optional[str] = Field(None, description='Name of the file the cif originated from')
    wavelength: Optional[float] = Field(None, description='Wavelength of the Characterizing Radiation')
    wavel_units: allowed_lengths = Field(None, description='Wavelength units in nm')
    q: Optional[Union[Array, str]] = Field(default_factory=list, description='Scattering Vector in Inverse nm')
    ttheta: Optional[Union[Array, str]] = Field(default_factory=list, description='Scattering Angle in Radians')
    intensity: Optional[Union[Array, str]] = Field(default_factory=list, description='Scattering Intensity')
    model_version: str = Field(
        MODEL_VERSION,
        alias='schema-version',
        description="Identifies the version of the pydantic powdercif model",
        read_only=True
    )

    def __init__(self, iucrid=None, x_units: str = None, x=None, y=None, **data):
        if "_id" not in data and "id" not in data:
            if iucrid is not None:
                try:
                    data["_id"] = ObjectId(iucrid)
                except InvalidId:
                    data["_id"] = ObjectId()
            else:
                data["_id"] = ObjectId()
        # ensure that x and y values are ndarrays, handling case of string from pycifrw
        if x is not None and y is not None:
            # if x and y not None, take this CIF ingestion route
            if isinstance(x[0], str):
                split = np.char.split(x, '(')
                x = np.array([float(e[0]) for e in split])
            elif isinstance(x[0], float):
                if isinstance(x, np.ndarray):
                    x = x
                else:
                    x = np.array(x)
            if isinstance(y[0], str):
                split = np.char.split(y, '(')
                data['intensity'] = np.array([float(e[0]) for e in split])
            elif isinstance(y[0], float):
                if isinstance(x, np.ndarray):
                    data['intensity'] = y
                else:
                    data['intensity'] = np.array(y)
            # set q and ttheta
            wavelength = data.get('wavelength', None)
            if wavelength:
                wavel_units = data.get('wavel_units', None)
                if wavel_units is None:
                    raise RuntimeError(
                        f"ERROR: Wavelength supplied without units. Wavelength units are required from {*LENGTHS,}.")
                if data['wavel_units'].lower() in ANGS:
                    wavelength = data['wavelength'] = wavelength / 10.
            if x_units is not None:
                if x_units.lower() in INVANGS:
                    data['q'] = np.array(x) * 10.
                    if wavelength:
                        data['ttheta'] = q_to_twotheta(data['q'], wavelength)
                elif x_units.lower() in INVNMS:
                    data['q'] = np.array(x)
                    if wavelength:
                        data['ttheta'] = q_to_twotheta(data['q'], wavelength)
                elif x_units in DEGS:
                    data['ttheta'] = np.array(np.radians(x))
                    if wavelength:
                        data['q'] = np.array(twotheta_to_q(data['ttheta'], wavelength))
                elif x_units in RADS:
                    data['ttheta'] = np.array(x)
                    if wavelength:
                        data['q'] = np.array(twotheta_to_q(data['ttheta'], wavelength))
        super().__init__(iucrid=iucrid, **data)

    class Config:
        allow_population_by_field_name = True
        underscore_attrs_are_private = False
        json_encoders = {
            **BSON_TYPES_ENCODERS,
            np.ndarray: json_gcs_export,
        }

    async def resolve_gcs_tokens(self):
        for array_token in ['q', 'ttheta', 'intensity']:
            val = getattr(self, array_token)
            if isinstance(val, str):
                val_str = val
            elif isinstance(val, np.ndarray):
                try:
                    val_str = str(val)
                except:
                    continue
            uuid4hex = re.compile('[0-9a-f]{32}\Z', re.I)
            if uuid4hex.match(val_str):
                array = await retrieve_glob_as_np(val_str)
                setattr(self, array_token, array)


class PowderCif:
    '''
    Attributes
    ----------
    wavelength : float
        The wavelength of the radiation, in units of nanometers
    q : numpy array
        The independent variable in quantity Q (wavevector amplitude) in units of
        inverse nanometers
    ttheta : numpy array
        The independent variable in quantity two-theta (scattering angle) in units of
        radians
    intensity : numpy array
        The intensity values
    iucrid string
      the unique identifier of the paper that the is associated with the data
    '''

    def __init__(self, iucrid, x_units, x, y, wavelength=None,
                 wavel_units=None):
        '''
        Powder Cif object constructor

        Parameters
        ----------
        iucrid string
          the unique identifier of the paper that the is associated with the data
        x_units string, from degrees, radians, invang, invnm
          the units of the x-array
        wavel_units string, from ang, angs, nm
          the units of the x-array
        x iterable
          the x-array.
        y iterable
          the intensity array
        wavelength float
          the wavelength.  Default is None
        '''
        self.iucrid = iucrid
        self.wavelength = wavelength
        if wavelength and not wavel_units:
            raise RuntimeError(
                f"ERROR: Wavelength supplied without units. Wavelength units are required from {*LENGTHS,}.")
        if self.wavelength:
            if wavel_units.lower() in ANGS:
                self.wavelength = wavelength / 10.
            elif wavel_units.lower() in NMS:
                self.wavelength = wavelength
            else:
                raise RuntimeError(
                    f"ERROR: Do not recognize units.  Select from {*LENGTHS,}")
        if x_units.lower() in INVANGS:
            self.q = np.array(x) * 10.
            if self.wavelength:
                self.ttheta = q_to_twotheta(self.q, self.wavelength)
        elif x_units.lower() in INVNMS:
            self.q = np.array(x)
            if self.wavelength:
                self.ttheta = q_to_twotheta(self.q, self.wavelength)
        elif x_units in DEGS:
            self.ttheta = np.array(np.radians(x))
            if self.wavelength:
                self.q = np.array(twotheta_to_q(self.ttheta, self.wavelength))
        elif x_units in RADS:
            self.ttheta = np.array(x)
            if self.wavelength:
                self.q = np.array(twotheta_to_q(self.ttheta, self.wavelength))
        else:
            raise RuntimeError(
                f"ERROR: Do not recognize units.  Select from {*INVS,}")
        self.intensity = np.array(y)
