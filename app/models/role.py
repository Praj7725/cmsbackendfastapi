from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.database import Base


class Role(Base):
    __tablename__ = "tbl_roles"

    role_id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("tbl_colleges.college_id"), nullable=False)

    role_code = Column(String(50), nullable=False)
    role_name = Column(String(100), nullable=False)
    description = Column(String(255))
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP)

    permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan"
    )
    # relationship to user roles
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
