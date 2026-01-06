from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional, List

from app.models.faculty import Faculty
from app.models.user import User
from app.models.college import College
from app.models.user_role import UserRole
from app.models.role import Role
from app.schemas.faculty_schema import FacultyCreate, FacultyUpdate

class FacultyService:

    @staticmethod
    def get_all_faculty(db: Session, college_id: Optional[int] = None):
        query = db.query(Faculty).options(
            joinedload(Faculty.user),
            joinedload(Faculty.college)
        )

        if college_id:
            query = query.filter(Faculty.college_id == college_id)

        faculty_list = query.all()

        return [
            {
                "faculty_id": f.faculty_id,
                "user_id": f.user_id,
                "full_name": f.user.username,
                "email": f.user.email,
                "phone": f.user.phone,
                "employee_code": f.employee_code,
                "designation": f.designation,
                "college_id": f.college_id,
                "college_name": f.college.college_name,
                "status": f.status,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "id": f.faculty_id
            }
            for f in faculty_list
        ]

    @staticmethod
    def get_faculty(db: Session, faculty_id: int):
        faculty = db.query(Faculty).options(
            joinedload(Faculty.user),
            joinedload(Faculty.college)
        ).filter(Faculty.faculty_id == faculty_id).first()

        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")

        return {
            "faculty_id": faculty.faculty_id,
            "user_id": faculty.user_id,
            "full_name": faculty.user.full_name,
            "email": faculty.user.email,
            "phone": faculty.user.phone,
            "employee_code": faculty.employee_code,
            "designation": faculty.designation,
            "college_id": faculty.college_id,
            "college_name": faculty.college.college_name,
            "status": faculty.status,
            "created_at": faculty.created_at.isoformat() if faculty.created_at else None,
            "id": faculty.faculty_id
        }

    @staticmethod
    def create_faculty(db: Session, data: FacultyCreate):
        user = db.query(User).filter(User.user_id == data.user_id).first()
        if not user:
            raise HTTPException(400, "Invalid user")
        # Ensure user has role Teacher or HOD
        ur = db.query(UserRole).filter(UserRole.user_id == user.user_id, UserRole.status == 1).order_by(UserRole.role_id).first()
        if not ur:
            raise HTTPException(400, "User has no active role")
        role = db.query(Role).filter(Role.role_id == ur.role_id).first()
        if not role or role.role_name not in ("Teacher", "HOD"):
            raise HTTPException(400, "User must have role Teacher or HOD")

        college = db.query(College).filter(College.college_id == data.college_id).first()
        if not college:
            raise HTTPException(404, "College not found")

        if db.query(Faculty).filter(Faculty.user_id == data.user_id).first():
            raise HTTPException(400, "User already assigned as faculty")

        if db.query(Faculty).filter(Faculty.employee_code == data.employee_code).first():
            raise HTTPException(400, "Employee code already exists")

        faculty = Faculty(**data.dict())

        try:
            db.add(faculty)
            db.commit()
            db.refresh(faculty)
        except IntegrityError:
            db.rollback()
            raise HTTPException(400, "Database error")

        return FacultyService.get_faculty(db, faculty.faculty_id)

    @staticmethod
    def update_faculty(db: Session, faculty_id: int, data: FacultyUpdate):
        faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
        if not faculty:
            raise HTTPException(404, "Faculty not found")

        updates = data.dict(exclude_unset=True)
        # if updating user_id ensure new user has appropriate role
        if "user_id" in updates:
            new_user = db.query(User).filter(User.user_id == updates["user_id"]).first()
            if not new_user:
                raise HTTPException(400, "Invalid user")
            ur = db.query(UserRole).filter(UserRole.user_id == new_user.user_id, UserRole.status == 1).order_by(UserRole.role_id).first()
            if not ur:
                raise HTTPException(400, "User has no active role")
            role = db.query(Role).filter(Role.role_id == ur.role_id).first()
            if not role or role.role_name not in ("Teacher", "HOD"):
                raise HTTPException(400, "User must have role Teacher or HOD")

        for key, value in updates.items():
            setattr(faculty, key, value)

        try:
            db.commit()
            db.refresh(faculty)
        except IntegrityError:
            db.rollback()
            raise HTTPException(400, "Database error")

        return FacultyService.get_faculty(db, faculty_id)

    @staticmethod
    def delete_faculty(db: Session, faculty_id: int):
        faculty = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
        if not faculty:
            raise HTTPException(404, "Faculty not found")

        faculty.status = 0
        db.commit()
        return {"message": "Faculty deactivated successfully"}
