from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class RolePermission(Base):
    __tablename__ = "tbl_role_permissions"

    role_id = Column(Integer, ForeignKey("tbl_roles.role_id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("tbl_permissions.permission_id"), primary_key=True)
    status = Column(Integer, default=1)
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission")
