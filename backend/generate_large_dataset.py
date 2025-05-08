import os
import random
import time
import argparse  # Add argparse for command line arguments
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from models.database import engine, Base
from models.contact import ContactDB, TransactionDB

# Parse command line arguments
parser = argparse.ArgumentParser(description='Generate large dataset for UBBank')
parser.add_argument('--recreate-db', action='store_true', help='Recreate the database from scratch')
parser.add_argument('--contacts', type=int, default=10000, help='Number of contacts to generate')
args = parser.parse_args()

# Initialize Faker
fake = Faker()

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Constants
BATCH_SIZE = 1000
TOTAL_CONTACTS = args.contacts  # Get from command line
MAX_TRANSACTIONS_PER_CONTACT = 10  # Max number of transactions per contact
MIN_TRANSACTIONS_PER_CONTACT = 1   # Min number of transactions per contact

# File to store timing information
TIME_FILE = os.path.abspath("time.txt")

def write_to_time_file(message):
    """Write a message to the time file"""
    # Print to console as well as file for debugging
    print(f"Writing to {TIME_FILE}: {message}")
    with open(TIME_FILE, "a") as f:
        f.write(f"{message}\n")
        f.flush()
        os.fsync(f.fileno())

def generate_tag(name, phone):
    """Generate a tag from name and phone"""
    if not name or not phone:
        return ""
    first_two = name[:2] if len(name) >= 2 else name
    last_two_digits = phone[-2:] if len(phone) >= 2 else phone
    last_two_name = name[-2:] if len(name) >= 2 else name
    return f"{first_two}{last_two_digits}{last_two_name}"

def generate_transaction_data(contact_id):
    """Generate random transaction data for a contact"""
    # Generate between MIN and MAX transactions
    num_transactions = random.randint(MIN_TRANSACTIONS_PER_CONTACT, MAX_TRANSACTIONS_PER_CONTACT)
    transactions = []
    
    for _ in range(num_transactions):
        # Random amount between -1000 and 1000
        amount = round(random.uniform(-1000, 1000), 2)
        
        # Random date within the last year
        days_back = random.randint(0, 365)
        date = datetime.now() - timedelta(days=days_back)
        
        # Random note
        note = fake.sentence(nb_words=5)
        
        transactions.append(TransactionDB(
            amount=amount,
            note=note,
            date=date,
            contact_id=contact_id
        ))
    
    # The last transaction is the latest one (chronologically)
    transactions.sort(key=lambda x: x.date, reverse=True)
    last_transaction = transactions[0].amount if transactions else 0
    
    return transactions, last_transaction

def generate_contacts_batch(db, batch_size, start_id):
    """Generate a batch of contacts with transactions"""
    try:
        batch_start_time = time.time()
        for i in range(batch_size):
            # Generate contact data
            name = fake.name()
            phone = f"07{random.randint(10000000, 99999999)}"
            email = fake.email()
            notes = fake.text(max_nb_chars=100)
            tag = generate_tag(name, phone)
            
            # Create contact
            contact = ContactDB(
                name=name,
                phone=phone,
                email=email,
                notes=notes,
                tag=tag,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Add to session
            db.add(contact)
            db.flush()  # This assigns the ID to the contact
            
            # Generate transactions for this contact
            transactions, last_transaction = generate_transaction_data(contact.id)
            
            # Update last transaction amount
            contact.last_transaction = last_transaction
            
            # Add transactions to session
            for transaction in transactions:
                db.add(transaction)
            
            # Commit in smaller batches to avoid memory issues
            if i % 100 == 0 and i > 0:
                db.commit()
        
        # Final commit for this batch
        db.commit()
        batch_time = time.time() - batch_start_time
        write_to_time_file(f"Batch completed in {batch_time:.2f} seconds - {batch_size} contacts")
        
    except Exception as e:
        db.rollback()
        write_to_time_file(f"Error generating batch: {e}")
        print(f"Error generating batch: {e}")
        raise

def drop_indices(db):
    """Drop indices before bulk insert for better performance"""
    try:
        index_time_start = time.time()
        db.execute(text("DROP INDEX IF EXISTS ix_contacts_id"))
        db.execute(text("DROP INDEX IF EXISTS ix_transactions_id"))
        db.commit()
        index_time = time.time() - index_time_start
        write_to_time_file(f"Indices dropped in {index_time:.2f} seconds")
        print("Indices dropped for faster insertion")
    except Exception as e:
        db.rollback()
        write_to_time_file(f"Error dropping indices: {e}")
        print(f"Error dropping indices: {e}")

def create_indices(db):
    """Create indices after bulk insert"""
    try:
        index_time_start = time.time()
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_contacts_id ON contacts(id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_transactions_id ON transactions(id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_transactions_contact_id ON transactions(contact_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_contacts_name ON contacts(name)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_contacts_email ON contacts(email)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_contacts_tag ON contacts(tag)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_transactions_date ON transactions(date)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_transactions_amount ON transactions(amount)"))
        db.commit()
        index_time = time.time() - index_time_start
        write_to_time_file(f"Indices created in {index_time:.2f} seconds")
        print("Indices created for better query performance")
    except Exception as e:
        db.rollback()
        write_to_time_file(f"Error creating indices: {e}")
        print(f"Error creating indices: {e}")

def main():
    """Main function to generate data"""
    # Clear the time file before starting
    with open(TIME_FILE, "w") as f:
        f.write(f"Data generation started at {datetime.now()}\n")
        f.write(f"Target: {TOTAL_CONTACTS} contacts\n")
        f.write(f"Batch size: {BATCH_SIZE}\n")
        f.write("-------------------------------------\n")
        f.flush()
        os.fsync(f.fileno())
    
    start_time = time.time()
    print(f"Starting generation of {TOTAL_CONTACTS} contacts...")
    write_to_time_file(f"Starting generation of {TOTAL_CONTACTS} contacts...")
    
    # If database is large, drop it first if requested
    if os.path.exists("ubbank.db"):
        db_size = os.path.getsize("ubbank.db") / (1024 * 1024)  # Size in MB
        write_to_time_file(f"Current database size: {db_size:.2f} MB")
        
        if args.recreate_db:  # Only recreate if explicitly requested
            print(f"Database is being recreated as requested...")
            write_to_time_file(f"Database is being recreated as requested...")
            os.remove("ubbank.db")
            Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Get current contact count
        current_count = db.query(ContactDB).count()
        print(f"Current contact count: {current_count}")
        write_to_time_file(f"Current contact count: {current_count}")
        
        # Calculate how many more contacts to generate
        contacts_to_generate = max(0, TOTAL_CONTACTS - current_count)
        print(f"Generating {contacts_to_generate} additional contacts...")
        write_to_time_file(f"Generating {contacts_to_generate} additional contacts...")
        
        if contacts_to_generate > 0:
            # Drop indices before bulk insert
            drop_indices(db)
            
            # Generate data in batches
            num_batches = contacts_to_generate // BATCH_SIZE
            if contacts_to_generate % BATCH_SIZE > 0:
                num_batches += 1
            
            for batch in range(num_batches):
                batch_size = min(BATCH_SIZE, contacts_to_generate - batch * BATCH_SIZE)
                print(f"Generating batch {batch+1}/{num_batches} ({batch_size} contacts)...")
                write_to_time_file(f"Starting batch {batch+1}/{num_batches} ({batch_size} contacts)...")
                batch_start = time.time()
                generate_contacts_batch(db, batch_size, current_count + batch * BATCH_SIZE)
                print(f"Batch {batch+1} completed in {time.time() - batch_start:.2f} seconds")
            
            # Create indices after bulk insert
            create_indices(db)
            
            # VACUUM to optimize database size
            vacuum_start = time.time()
            db.execute(text("VACUUM"))
            db.commit()
            vacuum_time = time.time() - vacuum_start
            write_to_time_file(f"VACUUM completed in {vacuum_time:.2f} seconds")
        
        # Generate some statistics
        contact_count = db.query(ContactDB).count()
        transaction_count = db.query(TransactionDB).count()
        
        write_to_time_file("\nFinal statistics:")
        write_to_time_file(f"Total contacts: {contact_count}")
        write_to_time_file(f"Total transactions: {transaction_count}")
        write_to_time_file(f"Average transactions per contact: {transaction_count / contact_count:.2f}")
        
        print(f"\nDatabase generation completed!")
        print(f"Total contacts: {contact_count}")
        print(f"Total transactions: {transaction_count}")
        print(f"Average transactions per contact: {transaction_count / contact_count:.2f}")
        
    except Exception as e:
        write_to_time_file(f"Error generating data: {e}")
        print(f"Error generating data: {e}")
    finally:
        db.close()
    
    total_time = time.time() - start_time
    write_to_time_file(f"\nTotal generation time: {total_time:.2f} seconds ({total_time / 60:.2f} minutes)")
    print(f"Total generation time: {total_time:.2f} seconds ({total_time / 60:.2f} minutes)")
    write_to_time_file(f"Data generation completed at {datetime.now()}")

if __name__ == "__main__":
    main() 

# python generate_large_dataset.py