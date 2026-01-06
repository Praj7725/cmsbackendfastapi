from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.services.role_service import get_roles_with_permissions, create_role
from app.services.permission_service import get_permission_by_code
from app.models.role_permission import RolePermission
from app.schemas.role import RoleCreate, RoleResponse


router = APIRouter(prefix="/admin/roles", tags=["Admin - Roles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[RoleResponse])
def list_roles(college_id: int, db: Session = Depends(get_db)):
    return get_roles_with_permissions(db, college_id)


@router.post("/", status_code=201)
def create_role_endpoint(data: RoleCreate, db: Session = Depends(get_db)):
    role = create_role(db, data.college_id, data.name, data.description)
    return {"message": "Role created", "role_id": role.role_id}


@router.post("/{role_id}/permissions")
def toggle_role_permission(
    role_id: int,
    permission_code: str,
    enabled: bool,
    db: Session = Depends(get_db)
):
    permission = get_permission_by_code(db, permission_code)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if enabled:
        # create or ensure exists
        db.merge(RolePermission(role_id=role_id, permission_id=permission.permission_id, status=1))
    else:
        db.query(RolePermission).filter(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission.permission_id
        ).delete()

    db.commit()
    return {"message": "Permission updated"}
