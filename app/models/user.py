from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "tbl_users"

    user_id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("tbl_colleges.college_id"))
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP)

    # relationships
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    faculty = relationship("Faculty", back_populates="user", uselist=False)
    college = relationship("College")
