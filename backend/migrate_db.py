import os
from models.database import Base, engine
from init_db import populate_initial_contacts

# Drop all tables
print("Dropping existing tables...")
Base.metadata.drop_all(bind=engine)

# Create all tables
print("Creating new tables with relationships...")
Base.metadata.create_all(bind=engine)

# Populate initial data
print("Populating database with sample data...")
populate_initial_contacts()

print("Database migration completed successfully!") 