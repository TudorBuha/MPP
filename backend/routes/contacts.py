from fastapi import APIRouter, HTTPException, Query, Depends, Path
from typing import List, Dict, Any, Optional
from backend.models.contact import ContactResponse, ContactCreate, ContactUpdate, TransactionCreate, Transaction
from backend.models.database import get_db
from store.db_store import db_store
from sqlalchemy.orm import Session
from datetime import datetime
import random
from utils.logging import log_action
from routes.auth import login
import jwt
from fastapi import Header

router = APIRouter()

# In-memory storage
contacts = []
next_id = 1

# Sample data for initial contacts
SAMPLE_NAMES = [
    "Tudor Buha", "Chis Denis", "Vlad Cenuse", "Maria Popescu", "Alex Dumitru",
    "Elena Ionescu", "Dan Marinescu", "Ana Popa", "Mihai Rusu", "Cristina Dobre",
    "George Stancu", "Laura Munteanu", "Adrian Preda", "Diana Florea", "Radu Ionita"
]

SAMPLE_NOTES = [
    "Best friend from high school", "College roommate", "Work colleague", 
    "Fitness instructor", "Business partner", "Yoga teacher", "Tennis partner",
    "Coffee shop regular", "Book club member", "Travel buddy", 
    "Photography enthusiast", "Music band member", "Hiking group leader",
    "Chess club friend", "Language exchange partner"
]

def generate_phone():
    return f"07{random.randint(10000000, 99999999)}"

def generate_email(name):
    name_parts = name.lower().split()
    return f"{name_parts[0]}.{name_parts[1]}@example.com"

def generate_tag(name, phone):
    first_two = name[:2]
    last_two_digits = phone[-2:]
    last_two_name = name[-2:]
    return f"{first_two}{last_two_digits}{last_two_name}"

def populate_initial_contacts():
    global next_id
    if not contacts:  # Only populate if the contacts list is empty
        for name, note in zip(SAMPLE_NAMES, SAMPLE_NOTES):
            phone = generate_phone()
            email = generate_email(name)
            tag = generate_tag(name, phone)
            last_transaction = random.uniform(-500, 500)
            
            contact = {
                "id": next_id,
                "name": name,
                "phone": phone,
                "email": email,
                "notes": note,
                "tag": tag,
                "last_transaction": round(last_transaction, 2),
                "transaction_history": [
                    {
                        "amount": round(last_transaction, 2),
                        "date": datetime.now(),
                        "note": "Initial transaction"
                    }
                ],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            contacts.append(contact)
            next_id += 1

# Initialize contacts
populate_initial_contacts()

# Helper to extract user_id from JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
def get_current_user_id(authorization: str = Header(...)):
    try:
        token = authorization.split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

@router.get("/contacts")
async def get_contacts(
    search: str = "",
    sort: str = "",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Pass pagination parameters directly to the database store
    contacts = db_store.get_all_contacts(db, search, sort, page, limit)
    
    # Get total count for pagination info
    total_count = db_store.get_contacts_count(db, search)
    
    # Return both the contacts and metadata
    return {
        "items": contacts,
        "total": total_count,
        "page": page,
        "limit": limit,
        "pages": (total_count + limit - 1) // limit  # Calculate total pages
    }

@router.get("/contacts/{contact_id}")
async def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db_store.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.post("/contacts")
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    # Generate tag if not provided
    if not contact.tag and contact.name and contact.phone:
        first_two = contact.name[:2] if len(contact.name) >= 2 else contact.name
        last_two_digits = contact.phone[-2:] if len(contact.phone) >= 2 else contact.phone
        last_two_name = contact.name[-2:] if len(contact.name) >= 2 else contact.name
        contact.tag = f"{first_two}{last_two_digits}{last_two_name}"
    
    new_contact = db_store.create_contact(db, contact)
    log_action(db, user_id, "create_contact", details=f"Contact ID: {new_contact['id']}")
    return new_contact

@router.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, contact_update: ContactUpdate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    updated_contact = db_store.update_contact(db, contact_id, contact_update)
    if not updated_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Update tag if name or phone changed
    if (contact_update.name or contact_update.phone) and updated_contact:
        name = updated_contact["name"]
        phone = updated_contact["phone"]
        
        first_two = name[:2] if len(name) >= 2 else name
        last_two_digits = phone[-2:] if len(phone) >= 2 else phone
        last_two_name = name[-2:] if len(name) >= 2 else name
        new_tag = f"{first_two}{last_two_digits}{last_two_name}"
        
        # Update the tag
        contact_update.tag = new_tag
        updated_contact = db_store.update_contact(db, contact_id, contact_update)
    
    log_action(db, user_id, "update_contact", details=f"Contact ID: {contact_id}")
    return updated_contact

@router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    success = db_store.delete_contact(db, contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    log_action(db, user_id, "delete_contact", details=f"Contact ID: {contact_id}")
    return {"message": "Contact deleted"}

@router.post("/contacts/{contact_id}/transaction")
async def add_transaction(
    contact_id: int = Path(..., description="Contact ID"),
    transaction: TransactionCreate = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    updated_contact = db_store.add_transaction(db, contact_id, transaction)
    if not updated_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    log_action(db, user_id, "add_transaction", details=f"Contact ID: {contact_id}")
    return updated_contact

@router.get("/contacts/{contact_id}/transactions")
async def get_transactions(
    contact_id: int = Path(..., description="Contact ID"),
    db: Session = Depends(get_db)
):
    """Get all transactions for a contact"""
    contact = db_store.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    transactions = db_store.get_transactions(db, contact_id)
    return transactions

@router.get("/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: int = Path(..., description="Transaction ID"),
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID"""
    transaction = db_store.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int = Path(..., description="Transaction ID"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a transaction by ID"""
    success = db_store.delete_transaction(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    log_action(db, user_id, "delete_transaction", details=f"Transaction ID: {transaction_id}")
    return {"message": "Transaction deleted"} 