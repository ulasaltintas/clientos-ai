
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel): #validates incoming company data
    name: str = Field(min_length=1, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)



class CompanyUpdate(BaseModel):
    name: str = Field(default=None, min_length=1, max_length=255)
    industry: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)


class CompanyResponse(CompanyCreate): #defines API response
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
