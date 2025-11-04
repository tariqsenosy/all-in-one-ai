from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    citizen_name = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    complaint_type = Column(String(50), nullable=True)
    action_taken = Column(String(100), nullable=True)
    reply = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
