from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from models.user import User
from models.activity_log import ActivityLog
from models.monitored_user import MonitoredUser
from utils.auth import get_password_hash

# Create engine and session
engine = create_engine("sqlite:///ubbank.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate_auth():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create admin user if it doesn't exist
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@ubbank.com",
                hashed_password=get_password_hash("admin123"),  # Change this in production!
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Created admin user")
        else:
            print("Admin user already exists")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_auth() 

# python migrate_auth.py