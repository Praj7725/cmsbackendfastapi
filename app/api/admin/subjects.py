from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import SessionLocal
from app.services.subject_service import (
    get_subjects,
    create_subject,
    update_subject,
    toggle_subject_status,
    delete_subject,
)
from app.schemas.subject_schema import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
)

router = APIRouter(prefix="/admin/subjects", tags=["Admin - Subjects"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[SubjectResponse])
def list_subjects(college_id: Optional[int] = None, course_id: Optional[int] = None, semester_id: Optional[int] = None, db: Session = Depends(get_db)):
    return get_subjects(db, college_id, course_id, semester_id)


@router.post("/", status_code=201)
def create_subject_endpoint(data: SubjectCreate, db: Session = Depends(get_db)):
    res = create_subject(db, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.put("/{subject_id}")
def update_subject_endpoint(subject_id: int, data: SubjectUpdate, db: Session = Depends(get_db)):
    res = update_subject(db, subject_id, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.patch("/{subject_id}/toggle-status")
def toggle_status(subject_id: int, db: Session = Depends(get_db)):
    res = toggle_subject_status(db, subject_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return res


@router.delete("/{subject_id}")
def remove_subject(subject_id: int, db: Session = Depends(get_db)):
    ok = delete_subject(db, subject_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"message": "Subject deleted (status set to inactive)"}
