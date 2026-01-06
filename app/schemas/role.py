from pydantic import BaseModel
from typing import Optional, List


class RoleCreate(BaseModel):
    college_id: int
    name: str
    description: Optional[str]


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    usersCount: int
    permissions: List[str]

    class Config:
        from_attributes = True
