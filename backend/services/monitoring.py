import threading
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from models.database import engine
from models.log import LogEntry
from models.monitored_user import MonitoredUser

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

THRESHOLD = 1  # actions
WINDOW_MINUTES = 0.3  # time window in minutes (30 seconds)


def monitor_logs():
    while True:
        db = SessionLocal()
        try:
            now = datetime.now()
            window_start = now - timedelta(minutes=WINDOW_MINUTES)
            # Count actions per user in the last WINDOW_MINUTES
            user_actions = (
                db.query(LogEntry.user_id)
                .filter(LogEntry.timestamp >= window_start)
                .all()
            )
            # Count actions per user
            from collections import Counter
            counts = Counter([ua[0] for ua in user_actions])
            for user_id, count in counts.items():
                if count > THRESHOLD:
                    # Check if already monitored
                    exists = db.query(MonitoredUser).filter_by(user_id=user_id).first()
                    if not exists:
                        monitored = MonitoredUser(user_id=user_id, reason=f"{count} actions in {WINDOW_MINUTES} min")
                        db.add(monitored)
                        db.commit()
        finally:
            db.close()
        time.sleep(10)  # Run every 30 seconds instead of 60

def start_monitoring_thread():
    t = threading.Thread(target=monitor_logs, daemon=True)
    t.start() 