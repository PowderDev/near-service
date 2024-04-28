from typing import Union, Dict, List

from pydantic import BaseModel


class HTTPSuccess(BaseModel):
    success: bool = True
    result: Union[Dict, List] = {}


class HTTPError(BaseModel):
    success: bool = False
    error: str = "Error description"
