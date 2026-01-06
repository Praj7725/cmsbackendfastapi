from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(Base):
    __tablename__ = "tbl_user_roles"

    user_id = Column(Integer, ForeignKey("tbl_users.user_id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("tbl_roles.role_id"), primary_key=True)
    status = Column(Integer, default=1)

    # relationships (safe, do not change DB schema)
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
