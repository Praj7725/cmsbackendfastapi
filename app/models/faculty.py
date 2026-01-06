from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Faculty(Base):
    __tablename__ = "tbl_faculty"

    faculty_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("tbl_users.user_id"), nullable=False)
    college_id = Column(Integer, ForeignKey("tbl_colleges.college_id"), nullable=False)
    employee_code = Column(String(50), unique=True, nullable=False)
    designation = Column(String(100))
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # 🔥 REQUIRED RELATIONSHIPS
    college = relationship("College")
    user = relationship("User")
