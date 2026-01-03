from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.college import College
from app.schemas.college import CollegeCreate

router = APIRouter(prefix="/admin/colleges", tags=["Admin - Colleges"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_colleges(db: Session = Depends(get_db)):
    colleges = db.query(College).all()
    return [
        {
            "id": c.college_id,
            "name": c.college_name,
            "code": c.college_code,
            "location": f"{c.city}, {c.state}" if c.city else "",
            "email": c.email,
            "phone": c.phone,
            "students": 0,
            "faculty": 0,
            "status": "active" if c.status == 1 else "inactive",
            "createdAt": c.created_at.strftime("%Y-%m-%d")
        }
        for c in colleges
    ]

@router.post("/")
def create_college(data: dict, db: Session = Depends(get_db)):
    college = College(
        college_name=data.get("college_name"),
        college_code=data.get("college_code"),
        college_type=data.get("college_type"),      # ✅ FIX
        affiliation=data.get("affiliation"),
        address=data.get("address"),
        city=data.get("city"),
        state=data.get("state"),
        pincode=data.get("pincode"),
        phone=data.get("phone"),
        email=data.get("email"),
        website=data.get("website"),
        established_year=data.get("established_year"),
        accreditation=data.get("accreditation"),
        status=data.get("status", 1),
    )

    db.add(college)
    db.commit()
    db.refresh(college)

    return {"message": "College created successfully"}


@router.put("/{college_id}")
def update_college(college_id: int, data: CollegeCreate, db: Session = Depends(get_db)):
    college = db.query(College).filter(College.college_id == college_id).first()
    if not college:
        raise HTTPException(404, "College not found")

    college.college_name = data.college_name
    college.college_code = data.college_code
    college.email = data.email
    college.phone = data.phone
    college.city = data.city
    college.state = data.state
    college.status = 1 if data.status == "active" else 0

    db.commit()
    return {"message": "College updated"}

@router.patch("/{college_id}/status")
def toggle_status(college_id: int, db: Session = Depends(get_db)):
    college = db.query(College).filter(College.college_id == college_id).first()
    if not college:
        raise HTTPException(404, "College not found")

    college.status = 0 if college.status == 1 else 1
    db.commit()
    return {"message": "Status updated"}
