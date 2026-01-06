from sqlalchemy import Column, Integer, String, TIMESTAMP
from app.core.database import Base


class Permission(Base):
    __tablename__ = "tbl_permissions"

    permission_id = Column(Integer, primary_key=True)
    permission_code = Column(String(100), unique=True, nullable=False)
    module = Column(String(100))
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP)
