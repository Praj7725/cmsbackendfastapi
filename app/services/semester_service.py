from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.semester import Semester


def get_semesters(db: Session, course_id: int):
    q = db.query(Semester).filter(Semester.course_id == course_id, Semester.status == 1).all()
    result = []
    for s in q:
        result.append({
            "semester_id": s.semester_id,
            "semester_number": int(s.semester_number) if s.semester_number is not None else 0,
            "semester_name": s.semester_name,
            "status": "active" if s.status == 1 else "inactive",
            "course_id": s.course_id,
            "course_name": s.course.course_name if getattr(s, "course", None) else None,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    return result


def create_semester(db: Session, data):
    # prevent duplicate semester_number per course
    exists = db.query(Semester).filter(Semester.course_id == data.course_id, Semester.semester_number == data.semester_number, Semester.status == 1).first()
    if exists:
        return {"error": "Semester number already exists for this course"}

    s = Semester(
        course_id=data.course_id,
        semester_number=data.semester_number,
        semester_name=data.semester_name,
        status=1 if data.status == "active" else 0,
    )
    db.add(s)
    db.commit()
    db.refresh(s)

    return {
        "semester_id": s.semester_id,
        "semester_number": s.semester_number,
        "semester_name": s.semester_name,
        "status": "active" if s.status == 1 else "inactive",
        "course_id": s.course_id,
        "course_name": s.course.course_name if getattr(s, "course", None) else None,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def update_semester(db: Session, semester_id: int, data):
    s = db.query(Semester).filter(Semester.semester_id == semester_id).first()
    if not s:
        return {"error": "Semester not found"}

    dup = db.query(Semester).filter(Semester.course_id == s.course_id, Semester.semester_number == data.semester_number, Semester.semester_id != semester_id, Semester.status == 1).first()
    if dup:
        return {"error": "Semester number already exists for this course"}

    s.semester_number = data.semester_number
    s.semester_name = data.semester_name
    s.status = 1 if data.status == "active" else 0
    db.commit()

    return {
        "semester_id": s.semester_id,
        "semester_number": s.semester_number,
        "semester_name": s.semester_name,
        "status": "active" if s.status == 1 else "inactive",
        "course_id": s.course_id,
        "course_name": s.course.course_name if getattr(s, "course", None) else None,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def toggle_semester_status(db: Session, semester_id: int):
    s = db.query(Semester).filter(Semester.semester_id == semester_id).first()
    if not s:
        return None
    s.status = 0 if s.status == 1 else 1
    db.commit()
    return {"message": "Status updated", "status": "active" if s.status == 1 else "inactive"}


def delete_semester(db: Session, semester_id: int):
    s = db.query(Semester).filter(Semester.semester_id == semester_id).first()
    if not s:
        return False
    s.status = 0
    db.commit()
    return True
