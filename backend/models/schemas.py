# backend/models/schemas.py
from pydantic import BaseModel

class DataResponse(BaseModel):
    """
    A generic response model for returning a URL to processed data.
    """
    topic: str
    region: str
    year: int
    data_url: str