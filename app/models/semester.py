from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Semester(Base):
    __tablename__ = "tbl_semesters"

    semester_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("tbl_courses.course_id"), nullable=False)
    semester_number = Column(Integer, nullable=False)
    semester_name = Column(String(255), nullable=False)
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())

    course = relationship("Course")
