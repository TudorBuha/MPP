from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import json
from datetime import datetime

from models.contact import ContactDB, ContactCreate, ContactUpdate, TransactionDB, TransactionCreate
from models.database import get_db

class DBStore:
    def get_all_contacts(self, db: Session, search: Optional[str] = None, sort_by: Optional[str] = None, 
                        page: Optional[int] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = db.query(ContactDB)
        
        # Apply search filter if provided
        if search:
            search = search.lower()
            query = query.filter(
                (ContactDB.name.ilike(f"%{search}%")) |
                (ContactDB.phone.ilike(f"%{search}%")) |
                (ContactDB.tag.ilike(f"%{search}%"))
            )
        
        # Apply sorting if provided
        if sort_by:
            reverse = False
            if sort_by.startswith('-'):
                reverse = True
                sort_by = sort_by[1:]
            
            if hasattr(ContactDB, sort_by):
                column = getattr(ContactDB, sort_by)
                query = query.order_by(column.desc() if reverse else column)
            else:
                # Default sort by id if invalid column
                query = query.order_by(ContactDB.id)
        else:
            # Default sort by id
            query = query.order_by(ContactDB.id)
        
        # Apply pagination at the database level if requested
        if page is not None and limit is not None:
            query = query.offset((page - 1) * limit).limit(limit)
        
        # Execute query and convert to dictionaries
        contacts = query.all()
        return [contact.to_dict() for contact in contacts]

    def get_contact(self, db: Session, contact_id: int) -> Optional[Dict[str, Any]]:
        contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if contact:
            return contact.to_dict()
        return None

    def create_contact(self, db: Session, contact: ContactCreate) -> Dict[str, Any]:
        new_contact = ContactDB(
            name=contact.name,
            phone=contact.phone,
            email=contact.email,
            notes=contact.notes,
            tag=contact.tag,
            last_transaction=contact.last_transaction,
            video_url=contact.video_url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return new_contact.to_dict()

    def update_contact(self, db: Session, contact_id: int, contact_data: ContactUpdate) -> Optional[Dict[str, Any]]:
        # Get existing contact
        contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not contact:
            return None
        
        # Update contact fields
        contact_dict = contact_data.model_dump(exclude_unset=True)
        for key, value in contact_dict.items():
            if key != "transaction_history" and value is not None:
                setattr(contact, key, value)
        
        contact.updated_at = datetime.now()
        db.commit()
        db.refresh(contact)
        return contact.to_dict()

    def delete_contact(self, db: Session, contact_id: int) -> bool:
        contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not contact:
            return False
        
        db.delete(contact)
        db.commit()
        return True

    def add_transaction(self, db: Session, contact_id: int, transaction_data: TransactionCreate) -> Optional[Dict[str, Any]]:
        # Get existing contact
        contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
        if not contact:
            return None
        
        # Create new transaction
        new_transaction = TransactionDB(
            amount=transaction_data.amount,
            note=transaction_data.note,
            date=datetime.now(),
            contact_id=contact_id
        )
        
        # Update last transaction on contact
        contact.last_transaction = transaction_data.amount
        contact.updated_at = datetime.now()
        
        # Save to database
        db.add(new_transaction)
        db.commit()
        db.refresh(contact)
        
        return contact.to_dict()
    
    def get_transactions(self, db: Session, contact_id: int) -> List[Dict[str, Any]]:
        """Get all transactions for a contact"""
        transactions = db.query(TransactionDB).filter(TransactionDB.contact_id == contact_id).all()
        return [t.to_dict() for t in transactions]
    
    def get_transaction(self, db: Session, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific transaction by ID"""
        transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
        if transaction:
            return transaction.to_dict()
        return None
        
    def delete_transaction(self, db: Session, transaction_id: int) -> bool:
        """Delete a transaction by ID"""
        transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
        if not transaction:
            return False
        
        db.delete(transaction)
        db.commit()
        return True

    def get_contacts_count(self, db: Session, search: Optional[str] = None) -> int:
        """Get the total count of contacts, applying any search filters"""
        query = db.query(ContactDB)
        
        # Apply search filter if provided
        if search:
            search = search.lower()
            query = query.filter(
                (ContactDB.name.ilike(f"%{search}%")) |
                (ContactDB.phone.ilike(f"%{search}%")) |
                (ContactDB.tag.ilike(f"%{search}%"))
            )
        
        # Return the count
        return query.count()

# Create a global instance of the store
db_store = DBStore() 