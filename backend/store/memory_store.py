from typing import List, Optional
from models.contact import Contact, ContactCreate

class MemoryStore:
    def __init__(self):
        self.contacts: List[Contact] = []
        self.counter = 1

    def get_all_contacts(self, search: Optional[str] = None, sort_by: Optional[str] = None) -> List[Contact]:
        filtered_contacts = self.contacts
        
        # Apply search filter if provided
        if search:
            search = search.lower()
            filtered_contacts = [
                contact for contact in filtered_contacts
                if search in contact.name.lower() or
                   search in contact.phone or
                   (contact.tag and search in contact.tag.lower())
            ]
        
        # Apply sorting if provided
        if sort_by:
            reverse = False
            if sort_by.startswith('-'):
                reverse = True
                sort_by = sort_by[1:]
            
            if hasattr(Contact, sort_by):
                filtered_contacts = sorted(
                    filtered_contacts,
                    key=lambda x: getattr(x, sort_by),
                    reverse=reverse
                )
        
        return filtered_contacts

    def get_contact(self, contact_id: int) -> Optional[Contact]:
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None

    def create_contact(self, contact: ContactCreate) -> Contact:
        new_contact = Contact(
            id=self.counter,
            **contact.model_dump()
        )
        self.contacts.append(new_contact)
        self.counter += 1
        return new_contact

    def update_contact(self, contact_id: int, contact_data: ContactCreate) -> Optional[Contact]:
        existing_contact = self.get_contact(contact_id)
        if existing_contact:
            updated_data = contact_data.model_dump()
            for key, value in updated_data.items():
                setattr(existing_contact, key, value)
            return existing_contact
        return None

    def delete_contact(self, contact_id: int) -> bool:
        contact = self.get_contact(contact_id)
        if contact:
            self.contacts.remove(contact)
            return True
        return False

    def update_transaction(self, contact_id: int, amount: float, note: str) -> Optional[Contact]:
        contact = self.get_contact(contact_id)
        if contact:
            contact.lastTransaction = amount
            transaction = {
                "amount": amount,
                "note": note,
                "date": "2024-03-28"  # In a real app, use actual datetime
            }
            contact.transactionHistory.insert(0, transaction)
            return contact
        return None

# Create a global instance of the store
store = MemoryStore() 