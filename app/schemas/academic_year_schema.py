from pydantic import BaseModel
from typing import Optional


class AcademicYearCreate(BaseModel):
    college_id: int
    year_code: str
    start_date: str
    end_date: str
    status: str = "active"


class AcademicYearUpdate(BaseModel):
    year_code: str
    start_date: str
    end_date: str
    status: str


class AcademicYearResponse(BaseModel):
    academic_year_id: int
    college_id: int
    college_name: Optional[str]
    year_code: str
    start_date: str
    end_date: str
    is_current: int
    status: str
    created_at: Optional[str]

    class Config:
        from_attributes = True
