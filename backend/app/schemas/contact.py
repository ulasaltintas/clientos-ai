
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ContactCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    job_title: str | None = Field(default=None, max_length=100)
    company_id: int = Field(gt=0)


class ContactResponse(ContactCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) #from_attributes allows Pydantic to serialize the SQLAlchemy Contact objects into JSON



class ContactUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    first_name: str = Field(default=None, min_length=1, max_length=100)
    last_name: str = Field(default=None, min_length=1, max_length=100)
    email: str = Field(default=None, min_length=1, max_length=255)

    phone: str | None = Field(default=None, max_length=20)
    job_title: str | None = Field(default=None, max_length=100)

    company_id: int = Field(default=None, gt=0)
