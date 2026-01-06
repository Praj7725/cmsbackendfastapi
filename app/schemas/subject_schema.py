from pydantic import BaseModel
from typing import Optional


class SubjectCreate(BaseModel):
    college_id: int
    course_id: int
    semester_id: int
    subject_code: str
    subject_name: str
    subject_type: str
    credits: Optional[float] = None
    status: str = "active"


class SubjectUpdate(BaseModel):
    subject_code: str
    subject_name: str
    subject_type: str
    credits: Optional[float] = None
    status: str


class SubjectResponse(BaseModel):
    subject_id: int
    subject_code: str
    subject_name: str
    subject_type: str
    credits: Optional[float]
    status: str
    course_id: int
    course_name: Optional[str]
    semester_id: int
    semester_name: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True
