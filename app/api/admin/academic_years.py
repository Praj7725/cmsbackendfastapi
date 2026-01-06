from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.services.academic_year_service import (
    get_academic_years,
    create_academic_year,
    update_academic_year,
    toggle_academic_year_status,
    set_current_academic_year,
    delete_academic_year,
)
from app.schemas.academic_year_schema import (
    AcademicYearCreate,
    AcademicYearUpdate,
    AcademicYearResponse,
)

router = APIRouter(prefix="/admin/academic-years", tags=["Admin - Academic Years"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[AcademicYearResponse])
def list_academic_years(college_id: int, db: Session = Depends(get_db)):
    return get_academic_years(db, college_id)


@router.post("/", status_code=201)
def create_academic_year_endpoint(data: AcademicYearCreate, db: Session = Depends(get_db)):
    res = create_academic_year(db, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.put("/{academic_year_id}")
def update_academic_year_endpoint(academic_year_id: int, data: AcademicYearUpdate, db: Session = Depends(get_db)):
    res = update_academic_year(db, academic_year_id, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.patch("/{academic_year_id}/toggle-status")
def toggle_status(academic_year_id: int, db: Session = Depends(get_db)):
    res = toggle_academic_year_status(db, academic_year_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Academic year not found")
    return res


@router.patch("/{academic_year_id}/set-current")
def set_current(academic_year_id: int, db: Session = Depends(get_db)):
    res = set_current_academic_year(db, academic_year_id)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=404, detail=res.get("error"))
    return res


@router.delete("/{academic_year_id}")
def remove_academic_year(academic_year_id: int, db: Session = Depends(get_db)):
    ok = delete_academic_year(db, academic_year_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Academic year not found")
    return {"message": "Academic year deleted (status set to inactive)"}
