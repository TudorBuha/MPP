import sqlite3

# Connect to the database
conn = sqlite3.connect('ubbank.db')
cursor = conn.cursor()

# Get the total number of contacts
cursor.execute('SELECT COUNT(*) FROM contacts')
total_contacts = cursor.fetchone()[0]
print(f"Total contacts in database: {total_contacts}")

# Get a sample of contacts from different parts of the ID range
ranges = [(1, 10), (1000, 1010), (5000, 5010), (10000, 10010), (50000, 50010), (90000, 90010)]
for start, end in ranges:
    cursor.execute(f'SELECT id, name FROM contacts WHERE id >= {start} AND id <= {end}')
    contacts = cursor.fetchall()
    print(f"\nContacts with IDs {start}-{end}:")
    for id, name in contacts:
        print(f"  ID: {id}, Name: {name}")

# Check total transactions
cursor.execute('SELECT COUNT(*) FROM transactions')
total_transactions = cursor.fetchone()[0]
print(f"\nTotal transactions in database: {total_transactions}")

# Close the connection
conn.close()

print("\nIf you're seeing contacts across different ID ranges, your database is populated correctly.")
print("The issue might be with pagination or sorting in the API or frontend.") 

# python check_db.py