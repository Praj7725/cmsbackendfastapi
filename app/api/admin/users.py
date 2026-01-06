from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.services.user_service import (
    get_users,
    create_user,
    update_user,
    toggle_user_status,
    delete_user,
)

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[UserResponse])
def list_users(role: Optional[str] = None, db: Session = Depends(get_db)):
    return get_users(db, role)

@router.post("/", response_model=UserResponse)
def create_new_user(data: UserCreate, db: Session = Depends(get_db)):
    res = create_user(db, data)
    if isinstance(res, dict) and res.get("error"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@router.put("/{user_id}", response_model=UserResponse)
def update_existing_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    res = update_user(db, user_id, data)
    if isinstance(res, dict) and res.get("error"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res

@router.patch("/{user_id}/toggle-status")
def toggle_status(user_id: int, db: Session = Depends(get_db)):
    return toggle_user_status(db, user_id)


@router.delete("/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db)):
    ok = delete_user(db, user_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}
