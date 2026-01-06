from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FacultyCreate(BaseModel):
    user_id: int
    college_id: int
    employee_code: str
    designation: str
    status: int = 1

class FacultyUpdate(BaseModel):
    user_id: Optional[int] = None
    college_id: Optional[int] = None
    employee_code: Optional[str] = None
    designation: Optional[str] = None
    status: Optional[int] = None

class FacultyResponse(BaseModel):
    faculty_id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str]
    employee_code: str
    designation: str
    college_id: int
    college_name: str
    status: int
    created_at: datetime

    
    class Config:
        from_attributes = True