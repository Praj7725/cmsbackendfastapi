from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.education_type import EducationType


def get_education_types(db: Session, college_id: int):
    q = db.query(EducationType).filter(EducationType.college_id == college_id, EducationType.status == 1).all()
    result = []
    for e in q:
        result.append({
            "education_type_id": e.education_type_id,
            "college_id": e.college_id,
            "college_name": e.college.college_name if getattr(e, "college", None) else None,
            "type_code": e.type_code,
            "type_name": e.type_name,
            "duration_years": int(e.duration_years),
            "status": "active" if e.status == 1 else "inactive",
            "created_at": e.created_at.isoformat() if e.created_at else None,
        })
    return result


def create_education_type(db: Session, data):
    exists = db.query(EducationType).filter(EducationType.college_id == data.college_id, func.lower(EducationType.type_code) == data.type_code.lower(), EducationType.status == 1).first()
    if exists:
        return {"error": "Type code already exists for this college"}

    et = EducationType(
        college_id=data.college_id,
        type_code=data.type_code,
        type_name=data.type_name,
        duration_years=data.duration_years,
        status=1 if data.status == "active" else 0,
    )
    db.add(et)
    db.commit()
    db.refresh(et)

    return {
        "education_type_id": et.education_type_id,
        "college_id": et.college_id,
        "type_code": et.type_code,
        "type_name": et.type_name,
        "duration_years": et.duration_years,
        "status": "active" if et.status == 1 else "inactive",
        "created_at": et.created_at.isoformat() if et.created_at else None,
    }


def update_education_type(db: Session, education_type_id: int, data):
    et = db.query(EducationType).filter(EducationType.education_type_id == education_type_id).first()
    if not et:
        return {"error": "Education type not found"}

    dup = db.query(EducationType).filter(EducationType.college_id == et.college_id, func.lower(EducationType.type_code) == data.type_code.lower(), EducationType.education_type_id != education_type_id, EducationType.status == 1).first()
    if dup:
        return {"error": "Type code already exists for this college"}

    et.type_code = data.type_code
    et.type_name = data.type_name
    et.duration_years = data.duration_years
    et.status = 1 if data.status == "active" else 0
    db.commit()

    return {
        "education_type_id": et.education_type_id,
        "college_id": et.college_id,
        "type_code": et.type_code,
        "type_name": et.type_name,
        "duration_years": et.duration_years,
        "status": "active" if et.status == 1 else "inactive",
        "created_at": et.created_at.isoformat() if et.created_at else None,
    }


def toggle_education_type_status(db: Session, education_type_id: int):
    et = db.query(EducationType).filter(EducationType.education_type_id == education_type_id).first()
    if not et:
        return None
    et.status = 0 if et.status == 1 else 1
    db.commit()
    return {"message": "Status updated", "status": "active" if et.status == 1 else "inactive"}


def delete_education_type(db: Session, education_type_id: int):
    et = db.query(EducationType).filter(EducationType.education_type_id == education_type_id).first()
    if not et:
        return False
    et.status = 0
    db.commit()
    return True
