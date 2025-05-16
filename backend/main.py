from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import asyncio
import json
import csv
from typing import List, Dict, Any
import os
from backend.routes.contacts import router as contacts_router
from backend.routes.analytics import router as analytics_router
from backend.routes.auth import router as auth_router
from backend.routes.admin import router as admin_router
from datetime import datetime
import io
from models.database import Base, engine
from models.contact import ContactCreate, TransactionCreate
from services.monitoring import start_monitoring_thread

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="UBBank API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # My Vue.js frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Create a copy of the list to safely iterate over
        connections = self.active_connections.copy()
        for connection in connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)
            except Exception:
                # Handle any other exceptions that might occur
                self.disconnect(connection)

manager = ConnectionManager()

# Background task for generating random contacts
async def generate_random_contacts():
    while True:
        await asyncio.sleep(10)  # Generate new contact every 10 seconds
        # Generate random contact logic here
        new_contact = {
            "name": "Auto Generated Contact",
            "phone": "1234567890",
            "email": "auto@example.com",
            "notes": "Generated automatically"
        }
        await manager.broadcast(json.dumps({"type": "new_contact", "data": new_contact}))

@app.on_event("startup")
async def startup_event():
    # Initialize database
    from init_db import populate_initial_contacts
    populate_initial_contacts()
    
    # Start WebSocket task
    asyncio.create_task(generate_random_contacts())
    # Start monitoring thread
    start_monitoring_thread()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    return {"filename": file.filename, "path": f"/uploads/{file.filename}"}

@app.get("/api/export-contacts")
async def export_contacts():
    export_path = UPLOAD_DIR / "contacts_export.csv"
    
    # Import the db_store to get all contacts
    from store.db_store import db_store
    from models.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Use get_all_contacts without pagination to get all contacts
        contacts = db_store.get_all_contacts(db, search="", sort_by="id")
        
        # Get the total count for logging
        total_count = db_store.get_contacts_count(db)
        print(f"Found {len(contacts)} contacts for export (total in DB: {total_count})")
        
        with open(export_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow([
                'ID', 'Name', 'Phone', 'Email', 'Notes', 'Tag', 
                'Last Transaction', 'Creation Date', 'Last Update'
            ])
            
            # Write data
            for contact in contacts:
                writer.writerow([
                    contact['id'],
                    contact['name'],
                    contact['phone'],
                    contact['email'],
                    contact['notes'],
                    contact['tag'],
                    contact['last_transaction'],
                    contact['created_at'],
                    contact['updated_at']
                ])
        
        return FileResponse(
            path=export_path, 
            filename="contacts_export.csv",
            media_type="text/csv"
        )
    finally:
        db.close()

@app.post("/api/import-contacts")
async def import_contacts(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Import necessary modules
    from models.contact import ContactCreate
    from store.db_store import db_store
    from models.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Read the CSV file
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        new_contacts = []
        
        # Process each row
        for row in csv_reader:
            # Validate required fields
            if not all(key in row for key in ['name', 'phone', 'email']):
                continue
                
            # Create contact object
            contact_data = ContactCreate(
                name=row['name'],
                phone=row['phone'],
                email=row['email'],
                notes=row.get('notes', ''),
                tag=row.get('tag', ''),
                last_transaction=float(row.get('last_transaction', 0))
            )
            
            # Add to database
            created_contact = db_store.create_contact(db, contact_data)
            
            # Add initial transaction if last_transaction is not 0
            if float(row.get('last_transaction', 0)) != 0:
                transaction_data = TransactionCreate(
                    amount=float(row.get('last_transaction', 0)),
                    note="Initial transaction from import"
                )
                db_store.add_transaction(db, created_contact['id'], transaction_data)
            
            new_contacts.append(created_contact)
            
        return {"message": f"Successfully imported {len(new_contacts)} contacts", "contacts": new_contacts}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to import contacts: {str(e)}")
    finally:
        db.close()

# Include the contacts router
app.include_router(contacts_router, prefix="/api")

# Include the analytics router
app.include_router(analytics_router, prefix="/api")

# Include the auth router
app.include_router(auth_router, prefix="/api/auth")

# Include the admin router
app.include_router(admin_router, prefix="/api/admin")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to UBBank API",
        "docs": "/docs",  # Swagger documentation
        "endpoints": {
            "contacts": "/api/contacts",
            "transactions": "/api/transactions",
            "analytics": "/api/statistics"
        }
    }

# To run the application:
#   1. Activate virtual environment:
#      Set-ExecutionPolicy Unrestricted -Scope Process
#      .\venv\Scripts\activate
#   
#   2. Install dependencies:
#      pip install fastapi uvicorn pydantic[email] python-multipart sqlalchemy
#
#   3. Run the server:
#      uvicorn main:app --reload

