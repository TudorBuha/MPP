from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.models.database import get_db
from backend.models.monitored_user import MonitoredUser
from backend.models.user import UserDB

router = APIRouter()

@router.get("/monitored-users")
async def get_monitored_users(db: Session = Depends(get_db)):
    monitored = db.query(MonitoredUser).all()
    result = []
    for m in monitored:
        user = db.query(UserDB).filter_by(id=m.user_id).first()
        result.append({
            "user_id": m.user_id,
            "username": user.username if user else None,
            "detected_at": m.detected_at,
            "reason": m.reason
        })
    return {"monitored_users": result}