from pydantic import BaseModel
from typing import Optional


class CourseCreate(BaseModel):
    college_id: int
    education_type_id: int
    course_code: str
    course_name: str
    duration_years: int
    total_semesters: int
    intake_capacity: Optional[int] = None
    status: str = "active"


class CourseUpdate(BaseModel):
    education_type_id: int
    course_code: str
    course_name: str
    duration_years: int
    total_semesters: int
    intake_capacity: Optional[int] = None
    status: str


class CourseResponse(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    duration_years: int
    total_semesters: int
    intake_capacity: Optional[int]
    status: str
    college_id: int
    college_name: Optional[str]
    education_type_id: int
    education_type_name: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True
