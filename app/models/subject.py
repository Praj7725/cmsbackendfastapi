from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Subject(Base):
    __tablename__ = "tbl_subjects"

    subject_id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("tbl_colleges.college_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("tbl_courses.course_id"), nullable=False)
    semester_id = Column(Integer, ForeignKey("tbl_semesters.semester_id"), nullable=False)
    subject_code = Column(String(100), nullable=False)
    subject_name = Column(String(255), nullable=False)
    subject_type = Column(String(50), nullable=False)
    credits = Column(Numeric(5,2), nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())

    course = relationship("Course")
    semester = relationship("Semester")
