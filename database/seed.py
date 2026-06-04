from database.db import SessionLocal
from database.models import Ticket, Incident, AccessRequest, Alert


db = SessionLocal()

ticket = Ticket(
    title="VPN Access Request",
    owner="kboller",
    status="Open",
)

incident = Incident(
    title="Database Connectivity Alert",
    severity="High",
    status="Investigating",
)

request = AccessRequest(
    username="kboller",
    system="vpn",
    action="grant",
    status="pending",
)

alert = Alert(
    source="monitoring",
    severity="High",
    title="Failed Login Spike",
    description="Multiple failed login attempts detected for one user.",
    status="Open",
)

db.add(ticket)
db.add(incident)
db.add(request)
db.add(alert)

db.commit()
db.close()

print("Sample data inserted.")