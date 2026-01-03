from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base

class College(Base):
    __tablename__ = "tbl_colleges"

    college_id = Column(Integer, primary_key=True, index=True)
    college_code = Column(String(20), unique=True, nullable=False)
    college_name = Column(String(255), nullable=False)
    college_type = Column(Enum("government", "private", "autonomous"))
    affiliation = Column(String(255))
    address = Column(String)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(255))
    established_year = Column(Integer)
    accreditation = Column(String(50))
    status = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
