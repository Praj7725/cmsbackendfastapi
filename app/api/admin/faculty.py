from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import SessionLocal
from app.schemas.faculty_schema import FacultyCreate, FacultyUpdate
from app.services.faculty_service import FacultyService
from app.api.auth import require_permissions

router = APIRouter(prefix="/admin/faculty", tags=["Admin - Faculty"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def list_faculty(college_id: Optional[int] = None, db: Session = Depends(get_db), deps: None = Depends(require_permissions(["faculty.view"]))):
    return FacultyService.get_all_faculty(db, college_id)

@router.post("/")
def create_faculty(data: FacultyCreate, db: Session = Depends(get_db), deps: None = Depends(require_permissions(["faculty.create"]))):
    return FacultyService.create_faculty(db, data)

@router.put("/{faculty_id}")
def update_faculty(faculty_id: int, data: FacultyUpdate, db: Session = Depends(get_db), deps: None = Depends(require_permissions(["faculty.edit"]))):
    return FacultyService.update_faculty(db, faculty_id, data)

@router.delete("/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_db), deps: None = Depends(require_permissions(["faculty.delete"]))):
    return FacultyService.delete_faculty(db, faculty_id)
