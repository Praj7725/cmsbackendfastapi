from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.subject import Subject


def get_subjects(db: Session, college_id: int = None, course_id: int = None, semester_id: int = None):
    q = db.query(Subject)
    if college_id is not None:
        q = q.filter(Subject.college_id == college_id)
    if course_id is not None:
        q = q.filter(Subject.course_id == course_id)
    if semester_id is not None:
        q = q.filter(Subject.semester_id == semester_id)
    q = q.filter(Subject.status == 1).all()

    result = []
    for s in q:
        result.append({
            "subject_id": s.subject_id,
            "subject_code": s.subject_code,
            "subject_name": s.subject_name,
            "subject_type": s.subject_type,
            "credits": float(s.credits) if s.credits is not None else None,
            "status": "active" if s.status == 1 else "inactive",
            "course_id": s.course_id,
            "course_name": s.course.course_name if getattr(s, "course", None) else None,
            "semester_id": s.semester_id,
            "semester_name": s.semester.semester_name if getattr(s, "semester", None) else None,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    return result


def create_subject(db: Session, data):
    # prevent duplicate subject_code per (college, course, semester)
    exists = db.query(Subject).filter(
        Subject.college_id == data.college_id,
        Subject.course_id == data.course_id,
        Subject.semester_id == data.semester_id,
        func.lower(Subject.subject_code) == data.subject_code.lower(),
        Subject.status == 1,
    ).first()
    if exists:
        return {"error": "Subject code already exists for this course/semester"}

    s = Subject(
        college_id=data.college_id,
        course_id=data.course_id,
        semester_id=data.semester_id,
        subject_code=data.subject_code,
        subject_name=data.subject_name,
        subject_type=data.subject_type,
        credits=data.credits,
        status=1 if data.status == "active" else 0,
    )
    db.add(s)
    db.commit()
    db.refresh(s)

    return {
        "subject_id": s.subject_id,
        "subject_code": s.subject_code,
        "subject_name": s.subject_name,
        "subject_type": s.subject_type,
        "credits": float(s.credits) if s.credits is not None else None,
        "status": "active" if s.status == 1 else "inactive",
        "course_id": s.course_id,
        "course_name": s.course.course_name if getattr(s, "course", None) else None,
        "semester_id": s.semester_id,
        "semester_name": s.semester.semester_name if getattr(s, "semester", None) else None,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def update_subject(db: Session, subject_id: int, data):
    s = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not s:
        return {"error": "Subject not found"}

    dup = db.query(Subject).filter(
        Subject.college_id == s.college_id,
        Subject.course_id == s.course_id,
        Subject.semester_id == s.semester_id,
        func.lower(Subject.subject_code) == data.subject_code.lower(),
        Subject.subject_id != subject_id,
        Subject.status == 1,
    ).first()
    if dup:
        return {"error": "Subject code already exists for this course/semester"}

    s.subject_code = data.subject_code
    s.subject_name = data.subject_name
    s.subject_type = data.subject_type
    s.credits = data.credits
    s.status = 1 if data.status == "active" else 0
    db.commit()

    return {
        "subject_id": s.subject_id,
        "subject_code": s.subject_code,
        "subject_name": s.subject_name,
        "subject_type": s.subject_type,
        "credits": float(s.credits) if s.credits is not None else None,
        "status": "active" if s.status == 1 else "inactive",
        "course_id": s.course_id,
        "course_name": s.course.course_name if getattr(s, "course", None) else None,
        "semester_id": s.semester_id,
        "semester_name": s.semester.semester_name if getattr(s, "semester", None) else None,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


def toggle_subject_status(db: Session, subject_id: int):
    s = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not s:
        return None
    s.status = 0 if s.status == 1 else 1
    db.commit()
    return {"message": "Status updated", "status": "active" if s.status == 1 else "inactive"}


def delete_subject(db: Session, subject_id: int):
    s = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not s:
        return False
    s.status = 0
    db.commit()
    return True
