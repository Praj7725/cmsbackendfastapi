from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.course import Course


def get_courses(db: Session, college_id: int):
    q = db.query(Course).filter(Course.college_id == college_id).all()
    result = []
    for c in q:
        result.append({
            "course_id": c.course_id,
            "course_code": c.course_code,
            "course_name": c.course_name,
            "duration_years": int(c.duration_years) if c.duration_years is not None else 0,
            "total_semesters": int(c.total_semesters) if c.total_semesters is not None else 0,
            "intake_capacity": int(c.intake_capacity) if c.intake_capacity is not None else None,
            "status": "active" if c.status == 1 else "inactive",
            "college_id": c.college_id,
            "college_name": c.college.college_name if getattr(c, "college", None) else None,
            "education_type_id": c.education_type_id,
            "education_type_name": c.education_type.type_name if getattr(c, "education_type", None) else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    return result


def create_course(db: Session, data):
    # prevent duplicate course_code per college (case-insensitive)
    exists = db.query(Course).filter(Course.college_id == data.college_id, func.lower(Course.course_code) == data.course_code.lower(), Course.status == 1).first()
    if exists:
        return {"error": "Course code already exists for this college"}

    c = Course(
        college_id=data.college_id,
        education_type_id=data.education_type_id,
        course_code=data.course_code,
        course_name=data.course_name,
        duration_years=data.duration_years,
        total_semesters=data.total_semesters,
        intake_capacity=data.intake_capacity,
        status=1 if data.status == "active" else 0,
    )
    db.add(c)
    db.commit()
    db.refresh(c)

    return {
        "course_id": c.course_id,
        "course_code": c.course_code,
        "course_name": c.course_name,
        "duration_years": c.duration_years,
        "total_semesters": c.total_semesters,
        "intake_capacity": c.intake_capacity,
        "status": "active" if c.status == 1 else "inactive",
        "college_id": c.college_id,
        "college_name": c.college.college_name if getattr(c, "college", None) else None,
        "education_type_id": c.education_type_id,
        "education_type_name": c.education_type.type_name if getattr(c, "education_type", None) else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def update_course(db: Session, course_id: int, data):
    c = db.query(Course).filter(Course.course_id == course_id).first()
    if not c:
        return {"error": "Course not found"}

    dup = db.query(Course).filter(Course.college_id == c.college_id, func.lower(Course.course_code) == data.course_code.lower(), Course.course_id != course_id, Course.status == 1).first()
    if dup:
        return {"error": "Course code already exists for this college"}

    c.education_type_id = data.education_type_id
    c.course_code = data.course_code
    c.course_name = data.course_name
    c.duration_years = data.duration_years
    c.total_semesters = data.total_semesters
    c.intake_capacity = data.intake_capacity
    c.status = 1 if data.status == "active" else 0
    db.commit()

    return {
        "course_id": c.course_id,
        "course_code": c.course_code,
        "course_name": c.course_name,
        "duration_years": c.duration_years,
        "total_semesters": c.total_semesters,
        "intake_capacity": c.intake_capacity,
        "status": "active" if c.status == 1 else "inactive",
        "college_id": c.college_id,
        "college_name": c.college.college_name if getattr(c, "college", None) else None,
        "education_type_id": c.education_type_id,
        "education_type_name": c.education_type.type_name if getattr(c, "education_type", None) else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def toggle_course_status(db: Session, course_id: int):
    c = db.query(Course).filter(Course.course_id == course_id).first()
    if not c:
        return None
    c.status = 0 if c.status == 1 else 1
    db.commit()
    return {"message": "Status updated", "status": "active" if c.status == 1 else "inactive"}


def delete_course(db: Session, course_id: int):
    c = db.query(Course).filter(Course.course_id == course_id).first()
    if not c:
        return False
    c.status = 0
    db.commit()
    return True
