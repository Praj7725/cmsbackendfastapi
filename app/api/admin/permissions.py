from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.services.permission_service import get_permissions
from app.schemas.permission import PermissionResponse


router = APIRouter(
    prefix="/admin/permissions",
    tags=["Admin - Permissions"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[PermissionResponse])
def list_permissions(db: Session = Depends(get_db)):
    permissions = get_permissions(db)
    if permissions is None:
        raise HTTPException(status_code=404, detail="Permissions not found")
    return permissions
