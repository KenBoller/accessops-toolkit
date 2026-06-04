from database.db import SessionLocal
from database.models import Ticket, Incident, AccessRequest


db = SessionLocal()

print("\nTickets:")
for ticket in db.query(Ticket).all():
    print(ticket.id, ticket.title, ticket.owner, ticket.status)

print("\nIncidents:")
for incident in db.query(Incident).all():
    print(incident.id, incident.title, incident.severity, incident.status)

print("\nAccess Requests:")
for request in db.query(AccessRequest).all():
    print(
        request.id,
        request.username,
        request.system,
        request.action,
        request.status,
        request.created_at,
    )

db.close()