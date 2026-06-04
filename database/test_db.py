from database.db import SessionLocal
from database.models import Ticket, Incident

db = SessionLocal()

print("\nTickets:")
for ticket in db.query(Ticket).all():
    print(ticket.id, ticket.title, ticket.owner, ticket.status)

print("\nIncidents:")
for incident in db.query(Incident).all():
    print(
        incident.id,
        incident.title,
        incident.severity,
        incident.status
    )

db.close()