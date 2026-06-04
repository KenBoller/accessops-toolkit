# database/test_db.py

from database.db import get_connection

conn = get_connection()
cursor = conn.cursor()

print("\nTickets:")
for row in cursor.execute("SELECT * FROM tickets"):
    print(dict(row))

print("\nIncidents:")
for row in cursor.execute("SELECT * FROM incidents"):
    print(dict(row))

conn.close()