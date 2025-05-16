from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from .database import Base

class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    details = Column(Text, nullable=True) 