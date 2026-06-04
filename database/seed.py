from database.db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
INSERT INTO tickets (title, owner, status)
VALUES (?, ?, ?)
""", (
    "VPN Access Request",
    "kboller",
    "Open"
))

cursor.execute("""
INSERT INTO incidents (title, severity, status)
VALUES (?, ?, ?)
""", (
    "Database Connectivity Alert",
    "High",
    "Investigating"
))

conn.commit()
conn.close()

print("Sample data inserted.")