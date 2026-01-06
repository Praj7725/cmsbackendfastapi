from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class EducationType(Base):
    __tablename__ = "tbl_education_types"

    education_type_id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("tbl_colleges.college_id"), nullable=False)
    type_code = Column(String(50), nullable=False)
    type_name = Column(String(255), nullable=False)
    duration_years = Column(Integer, default=0)
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())

    college = relationship("College")
