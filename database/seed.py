from database.db import SessionLocal
from database.models import Ticket, Incident

db = SessionLocal()

ticket = Ticket(
    title="VPN Access Request",
    owner="kboller",
    status="Open"
)

incident = Incident(
    title="Database Connectivity Alert",
    severity="High",
    status="Investigating"
)

db.add(ticket)
db.add(incident)

db.commit()
db.close()

print("Sample data inserted.")