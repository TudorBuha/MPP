from models.database import Base, engine
from models.contact import ContactDB, TransactionDB
from sqlalchemy.orm import Session
import random
from datetime import datetime, timedelta
import json

# Create all tables
Base.metadata.create_all(bind=engine)

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

TRANSACTION_NOTES = [
    "Monthly payment", "Loan repayment", "Dinner", "Movie tickets",
    "Gift", "Shared bill", "Rent", "Groceries", "Utility bill",
    "Transportation", "Coffee", "Online purchase", "Subscription",
    "Medical expense", "Entertainment"
]

def generate_phone():
    return f"07{random.randint(10000000, 99999999)}"

def generate_email(name):
    name_parts = name.lower().split()
    return f"{name_parts[0]}.{name_parts[1]}@example.com"

def generate_tag(name, phone):
    first_two = name[:2] if name else ""
    last_two_digits = phone[-2:] if phone else ""
    last_two_name = name[-2:] if name else ""
    return f"{first_two}{last_two_digits}{last_two_name}"

def generate_random_transactions(db, contact_id, num_transactions=5):
    """Generate random transactions for a contact"""
    transactions = []
    now = datetime.now()
    
    for i in range(num_transactions):
        # Generate a random amount between -500 and 500
        amount = round(random.uniform(-500, 500), 2)
        
        # Generate a random date within the last 30 days
        random_days = random.randint(0, 30)
        transaction_date = now - timedelta(days=random_days)
        
        # Create the transaction
        transaction = TransactionDB(
            amount=amount,
            note=random.choice(TRANSACTION_NOTES),
            date=transaction_date,
            contact_id=contact_id
        )
        db.add(transaction)
        transactions.append(transaction)
    
    return transactions

def populate_initial_contacts():
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Check if we already have contacts
    existing_contacts = db.query(ContactDB).count()
    if existing_contacts > 0:
        print(f"Database already contains {existing_contacts} contacts. Skipping initialization.")
        db.close()
        return

    try:
        print("Creating sample contacts with transactions...")
        added_contacts = []
        
        for name, note in zip(SAMPLE_NAMES, SAMPLE_NOTES):
            phone = generate_phone()
            email = generate_email(name)
            tag = generate_tag(name, phone)
            last_transaction = round(random.uniform(-500, 500), 2)
            
            contact = ContactDB(
                name=name,
                phone=phone,
                email=email,
                notes=note,
                tag=tag,
                last_transaction=last_transaction,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(contact)
            db.flush()  # This assigns the ID to the contact
            
            # Now create transactions for this contact
            transactions = generate_random_transactions(db, contact.id)
            added_contacts.append(contact)
        
        db.commit()
        print(f"Successfully added {len(added_contacts)} sample contacts with transactions!")
    except Exception as e:
        db.rollback()
        print(f"Error populating database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    populate_initial_contacts()
    print("Database initialization completed!") 