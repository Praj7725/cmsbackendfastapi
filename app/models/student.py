from sqlalchemy import Column, Integer, String, ForeignKey, Year, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base

class Student(Base):
    __tablename__ = "tbl_students"

    student_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("tbl_users.user_id"), unique=True)
    college_id = Column(Integer, ForeignKey("tbl_colleges.college_id"))
    admission_number = Column(String(50), unique=True, nullable=False)
    admission_year = Column(Year, nullable=False)
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
