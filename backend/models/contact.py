from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# SQLAlchemy ORM model for Transaction
class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    note = Column(String(255), nullable=True)
    date = Column(DateTime, default=datetime.now)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"))
    
    # Relationship to Contact
    contact = relationship("ContactDB", back_populates="transactions")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "amount": self.amount,
            "note": self.note,
            "date": self.date,
            "contact_id": self.contact_id
        }

# SQLAlchemy ORM model for Contact
class ContactDB(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)
    email = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)
    tag = Column(String(50), nullable=True)
    last_transaction = Column(Float, default=0)
    video_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship to Transaction - one-to-many (one contact can have many transactions)
    transactions = relationship("TransactionDB", back_populates="contact", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "notes": self.notes,
            "tag": self.tag,
            "last_transaction": self.last_transaction,
            "transaction_history": [t.to_dict() for t in self.transactions],
            "video_url": self.video_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Pydantic models for API validation
class Transaction(BaseModel):
    id: Optional[int] = None
    amount: float
    date: datetime
    note: Optional[str] = None
    contact_id: Optional[int] = None

class TransactionCreate(BaseModel):
    amount: float
    note: Optional[str] = None

class ContactBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    email: EmailStr
    notes: Optional[str] = None
    tag: Optional[str] = None
    last_transaction: float = Field(default=0)
    video_url: Optional[str] = None

    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip().replace(' ', '')
        if not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number format')
        return v

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{10,15}$')
    email: Optional[EmailStr] = None

class ContactResponse(ContactBase):
    id: int
    created_at: datetime
    updated_at: datetime
    transaction_history: List[Transaction] = []

    class Config:
        from_attributes = True 