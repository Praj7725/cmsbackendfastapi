from pydantic import BaseModel
from typing import Optional


class SemesterCreate(BaseModel):
    course_id: int
    semester_number: int
    semester_name: str
    status: str = "active"


class SemesterUpdate(BaseModel):
    semester_number: int
    semester_name: str
    status: str


class SemesterResponse(BaseModel):
    semester_id: int
    semester_number: int
    semester_name: str
    status: str
    course_id: int
    course_name: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True
