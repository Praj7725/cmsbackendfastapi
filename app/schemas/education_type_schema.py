from pydantic import BaseModel
from typing import Optional


class EducationTypeCreate(BaseModel):
    college_id: int
    type_code: str
    type_name: str
    duration_years: int
    status: str = "active"


class EducationTypeUpdate(BaseModel):
    type_code: str
    type_name: str
    duration_years: int
    status: str


class EducationTypeResponse(BaseModel):
    education_type_id: int
    college_id: int
    college_name: Optional[str]
    type_code: str
    type_name: str
    duration_years: int
    status: str
    created_at: Optional[str]

    class Config:
        from_attributes = True
