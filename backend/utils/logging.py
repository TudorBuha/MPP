from models.log import LogEntry
from sqlalchemy.orm import Session
from typing import Optional

def log_action(db: Session, user_id: int, action: str, details: Optional[str] = None):
    log = LogEntry(user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit() 