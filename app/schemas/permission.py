from pydantic import BaseModel
from typing import Optional


class PermissionResponse(BaseModel):
    permission_id: int
    permission_code: str
    module: Optional[str]
    status: int

    class Config:
        from_attributes = True
