from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str]
    role_id: int
    college_id: int
    status: str = "active"


class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str]
    role_id: int
    college_id: int
    status: str


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    role_id: int
    role_name: str
    college_id: int
    college_name: str
    status: str
    created_at: Optional[str]

    class Config:
        from_attributes = True
