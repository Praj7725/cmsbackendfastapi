from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.services.education_type_service import (
    get_education_types,
    create_education_type,
    update_education_type,
    toggle_education_type_status,
    delete_education_type,
)
from app.schemas.education_type_schema import (
    EducationTypeCreate,
    EducationTypeUpdate,
    EducationTypeResponse,
)

router = APIRouter(prefix="/admin/education-types", tags=["Admin - Education Types"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[EducationTypeResponse])
def list_education_types(college_id: int, db: Session = Depends(get_db)):
    return get_education_types(db, college_id)


@router.post("/", status_code=201)
def create_education_type_endpoint(data: EducationTypeCreate, db: Session = Depends(get_db)):
    res = create_education_type(db, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.put("/{education_type_id}")
def update_education_type_endpoint(education_type_id: int, data: EducationTypeUpdate, db: Session = Depends(get_db)):
    res = update_education_type(db, education_type_id, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.patch("/{education_type_id}/toggle-status")
def toggle_status(education_type_id: int, db: Session = Depends(get_db)):
    res = toggle_education_type_status(db, education_type_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Education type not found")
    return res


@router.delete("/{education_type_id}")
def remove_education_type(education_type_id: int, db: Session = Depends(get_db)):
    ok = delete_education_type(db, education_type_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Education type not found")
    return {"message": "Education type deleted (status set to inactive)"}
