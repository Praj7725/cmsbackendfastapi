from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.services.semester_service import (
    get_semesters,
    create_semester,
    update_semester,
    toggle_semester_status,
    delete_semester,
)
from app.schemas.semester_schema import (
    SemesterCreate,
    SemesterUpdate,
    SemesterResponse,
)

router = APIRouter(prefix="/admin/semesters", tags=["Admin - Semesters"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[SemesterResponse])
def list_semesters(course_id: int, db: Session = Depends(get_db)):
    return get_semesters(db, course_id)


@router.post("/", status_code=201)
def create_semester_endpoint(data: SemesterCreate, db: Session = Depends(get_db)):
    res = create_semester(db, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.put("/{semester_id}")
def update_semester_endpoint(semester_id: int, data: SemesterUpdate, db: Session = Depends(get_db)):
    res = update_semester(db, semester_id, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.patch("/{semester_id}/toggle-status")
def toggle_status(semester_id: int, db: Session = Depends(get_db)):
    res = toggle_semester_status(db, semester_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Semester not found")
    return res


@router.delete("/{semester_id}")
def remove_semester(semester_id: int, db: Session = Depends(get_db)):
    ok = delete_semester(db, semester_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Semester not found")
    return {"message": "Semester deleted (status set to inactive)"}
