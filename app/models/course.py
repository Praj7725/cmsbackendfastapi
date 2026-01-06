from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Course(Base):
    __tablename__ = "tbl_courses"

    course_id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("tbl_colleges.college_id"), nullable=False)
    education_type_id = Column(Integer, ForeignKey("tbl_education_types.education_type_id"), nullable=False)
    course_code = Column(String(50), nullable=False)
    course_name = Column(String(255), nullable=False)
    duration_years = Column(Integer, default=0)
    total_semesters = Column(Integer, default=0)
    intake_capacity = Column(Integer, nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())

    college = relationship("College")
    education_type = relationship("EducationType")
