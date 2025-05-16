from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class MonitoredUser(Base):
    __tablename__ = "monitored_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    detected_at = Column(DateTime, default=datetime.now)
    reason = Column(String(255), nullable=False) 