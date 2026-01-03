from pydantic import BaseModel, EmailStr
from typing import Optional

class CollegeCreate(BaseModel):
    college_code: str
    college_name: str
    college_type: str
    email: Optional[EmailStr]
    phone: Optional[str]
    website: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    affiliation: Optional[str]
    accreditation: Optional[str]
    established_year: Optional[int]
    status: int = 1

class CollegeResponse(BaseModel):
    college_id: int
    college_name: str
    college_code: str
    status: int

    class Config:
        orm_mode = True
