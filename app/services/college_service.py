from sqlalchemy.orm import Session
from app.models.college import College
from app.schemas.college import CollegeCreate

def create_college(db: Session, data: CollegeCreate):
    exists = db.query(College).filter(
        College.college_code == data.college_code
    ).first()

    if exists:
        raise ValueError("College code already exists")

    college = College(**data.dict())
    db.add(college)
    db.commit()
    db.refresh(college)
    return college

def get_colleges(db: Session):
    return db.query(College).filter(College.status == 1).all()

def update_college_status(db: Session, college_id: int, status: int):
    college = db.query(College).filter(College.college_id == college_id).first()
    if not college:
        return None
    college.status = status
    db.commit()
    return college
