from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.services.course_service import (
    get_courses,
    create_course,
    update_course,
    toggle_course_status,
    delete_course,
)
from app.schemas.course_schema import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
)

router = APIRouter(prefix="/admin/courses", tags=["Admin - Courses"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[CourseResponse])
def list_courses(college_id: int, db: Session = Depends(get_db)):
    return get_courses(db, college_id)


@router.post("/", status_code=201)
def create_course_endpoint(data: CourseCreate, db: Session = Depends(get_db)):
    res = create_course(db, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.put("/{course_id}")
def update_course_endpoint(course_id: int, data: CourseUpdate, db: Session = Depends(get_db)):
    res = update_course(db, course_id, data)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@router.patch("/{course_id}/toggle-status")
def toggle_status(course_id: int, db: Session = Depends(get_db)):
    res = toggle_course_status(db, course_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return res


@router.delete("/{course_id}")
def remove_course(course_id: int, db: Session = Depends(get_db)):
    ok = delete_course(db, course_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted (status set to inactive)"}
