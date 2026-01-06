from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.academic_year import AcademicYear
from app.models.college import College
from datetime import datetime


def get_academic_years(db: Session, college_id: int):
    q = db.query(AcademicYear).filter(AcademicYear.college_id == college_id, AcademicYear.status == 1).all()
    result = []
    for a in q:
        result.append({
            "academic_year_id": a.academic_year_id,
            "college_id": a.college_id,
            "college_name": a.college.college_name if getattr(a, "college", None) else None,
            "year_code": a.year_code,
            "start_date": a.start_date.isoformat() if a.start_date else None,
            "end_date": a.end_date.isoformat() if a.end_date else None,
            "is_current": int(a.is_current),
            "status": "active" if a.status == 1 else "inactive",
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })
    return result


def create_academic_year(db: Session, data):
    # prevent duplicate year_code per college
    exists = db.query(AcademicYear).filter(AcademicYear.college_id == data.college_id, func.lower(AcademicYear.year_code) == data.year_code.lower(), AcademicYear.status == 1).first()
    if exists:
        return {"error": "Academic year code already exists for this college"}

    # parse dates
    try:
        sd = datetime.fromisoformat(data.start_date).date()
        ed = datetime.fromisoformat(data.end_date).date()
    except Exception:
        sd = None
        ed = None

    ay = AcademicYear(
        college_id=data.college_id,
        year_code=data.year_code,
        start_date=sd,
        end_date=ed,
        status=1 if data.status == "active" else 0,
        is_current=0,
    )
    db.add(ay)
    db.commit()
    db.refresh(ay)

    return {
        "academic_year_id": ay.academic_year_id,
        "college_id": ay.college_id,
        "year_code": ay.year_code,
        "start_date": ay.start_date.isoformat() if ay.start_date else None,
        "end_date": ay.end_date.isoformat() if ay.end_date else None,
        "is_current": int(ay.is_current),
        "status": "active" if ay.status == 1 else "inactive",
        "created_at": ay.created_at.isoformat() if ay.created_at else None,
    }


def update_academic_year(db: Session, academic_year_id: int, data):
    ay = db.query(AcademicYear).filter(AcademicYear.academic_year_id == academic_year_id).first()
    if not ay:
        return {"error": "Academic year not found"}

    # check duplicate
    dup = db.query(AcademicYear).filter(AcademicYear.college_id == ay.college_id, func.lower(AcademicYear.year_code) == data.year_code.lower(), AcademicYear.academic_year_id != academic_year_id, AcademicYear.status == 1).first()
    if dup:
        return {"error": "Academic year code already exists for this college"}

    ay.year_code = data.year_code
    try:
        ay.start_date = datetime.fromisoformat(data.start_date).date()
        ay.end_date = datetime.fromisoformat(data.end_date).date()
    except Exception:
        ay.start_date = data.start_date
        ay.end_date = data.end_date
    ay.status = 1 if data.status == "active" else 0
    db.commit()

    return {
        "academic_year_id": ay.academic_year_id,
        "college_id": ay.college_id,
        "year_code": ay.year_code,
        "start_date": ay.start_date.isoformat() if ay.start_date else None,
        "end_date": ay.end_date.isoformat() if ay.end_date else None,
        "is_current": int(ay.is_current),
        "status": "active" if ay.status == 1 else "inactive",
        "created_at": ay.created_at.isoformat() if ay.created_at else None,
    }


def toggle_academic_year_status(db: Session, academic_year_id: int):
    ay = db.query(AcademicYear).filter(AcademicYear.academic_year_id == academic_year_id).first()
    if not ay:
        return None
    ay.status = 0 if ay.status == 1 else 1
    db.commit()
    return {"message": "Status updated", "status": "active" if ay.status == 1 else "inactive"}


def set_current_academic_year(db: Session, academic_year_id: int):
    ay = db.query(AcademicYear).filter(AcademicYear.academic_year_id == academic_year_id).first()
    if not ay:
        return {"error": "Academic year not found"}

    # set other years of same college to is_current = 0
    db.query(AcademicYear).filter(AcademicYear.college_id == ay.college_id).update({"is_current": 0})
    ay.is_current = 1
    db.commit()
    return {"message": "Set as current"}


def delete_academic_year(db: Session, academic_year_id: int):
    ay = db.query(AcademicYear).filter(AcademicYear.academic_year_id == academic_year_id).first()
    if not ay:
        return False
    # soft delete
    ay.status = 0
    db.commit()
    return True
