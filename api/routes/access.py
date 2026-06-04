"""
AccessOps Toolkit - Access API Routes
-------------------------------------
REST endpoints for system discovery, access checks, grants, removals,
platform summary stats, and ticket CRUD operations.
"""

from pathlib import Path
import json
import sys

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.db import SessionLocal
from database.models import Ticket, Incident, AccessRequest, Alert

from datetime import datetime


PROJECT_DIR = Path(__file__).resolve().parents[2]

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from access_management import (  # noqa: E402
    check_access,
    discover_system_scripts,
    grant_access,
    remove_access,
)


router = APIRouter(
    prefix="/api",
    tags=["Access Management"],
)


class AccessActionResponse(BaseModel):
    status: str
    username: str
    system: str
    action: str
    mock: bool
    dry_run: bool


class AccessCheckResponse(BaseModel):
    username: str
    systems_checked: int
    access_found_count: int
    access_found: list[str]


class SystemsResponse(BaseModel):
    count: int
    systems: list[str]


class StatsResponse(BaseModel):
    systems_available: int
    users_tracked: int
    tickets_open: int
    incidents_open: int
    access_requests_pending: int


class TicketCreate(BaseModel):
    title: str
    owner: str | None = None
    status: str = "Open"


class TicketUpdate(BaseModel):
    title: str | None = None
    owner: str | None = None
    status: str | None = None


class TicketResponse(BaseModel):
    id: int
    title: str
    owner: str | None
    status: str

    class Config:
        from_attributes = True


class IncidentResponse(BaseModel):
    id: int
    title: str
    severity: str | None
    status: str

    class Config:
        from_attributes = True


class AccessRequestResponse(BaseModel):
    id: int
    username: str
    system: str
    action: str
    status: str
    created_at: str | None = None

class AlertCreate(BaseModel):
    source: str
    severity: str = "Medium"
    title: str
    description: str | None = None
    status: str = "Open"


class AlertUpdate(BaseModel):
    source: str | None = None
    severity: str | None = None
    title: str | None = None
    description: str | None = None
    status: str | None = None


class AlertResponse(BaseModel):
    id: int
    source: str
    severity: str
    title: str
    description: str | None
    status: str

    class Config:
        from_attributes = True


def get_available_systems() -> dict[str, str]:
    """Return discovered systems keyed by normalized system name."""
    return discover_system_scripts()


def validate_system(system: str) -> str:
    """Validate that a requested system exists."""
    system_name = system.lower()
    available_systems = get_available_systems()

    if system_name not in available_systems:
        raise HTTPException(
            status_code=404,
            detail=f"System not found: {system}",
        )

    return system_name


def load_json_file(file_path: Path, default):
    """Safely load a JSON file, returning a default value if missing or invalid."""
    if not file_path.exists():
        return default

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return default


@router.get("/systems", response_model=SystemsResponse)
def get_systems() -> SystemsResponse:
    """Return all discovered access-managed systems."""
    systems = sorted(get_available_systems().keys())

    return SystemsResponse(
        count=len(systems),
        systems=systems,
    )


@router.get("/stats", response_model=StatsResponse)
def get_stats() -> StatsResponse:
    """Return high-level AccessOps platform stats."""
    systems = get_available_systems()

    data_dir = PROJECT_DIR / "data"
    access_state_file = data_dir / "access_state.json"

    users_tracked = 0

    access_state = load_json_file(access_state_file, {})
    tracked_users = set()

    if isinstance(access_state, dict):
        for system_users in access_state.values():
            if isinstance(system_users, dict):
                tracked_users.update(system_users.keys())

    users_tracked = len(tracked_users)

    db = SessionLocal()

    try:
        tickets_open = db.query(Ticket).filter(Ticket.status == "Open").count()

        incidents_open = (
            db.query(Incident)
            .filter(Incident.status.in_(["Open", "Active", "Triggered", "Investigating"]))
            .count()
        )

        access_requests_pending = (
            db.query(AccessRequest)
            .filter(AccessRequest.status.in_(["pending", "pending_approval"]))
            .count()
        )

        return StatsResponse(
            systems_available=len(systems),
            users_tracked=users_tracked,
            tickets_open=tickets_open,
            incidents_open=incidents_open,
            access_requests_pending=access_requests_pending,
        )

    finally:
        db.close()


@router.get("/users/{username}/access", response_model=AccessCheckResponse)
def get_user_access(username: str, system: str | None = None) -> AccessCheckResponse:
    """Check access for a user. Optional query parameter: ?system=jira"""
    available_systems = get_available_systems()

    normalized_system = None

    if system:
        normalized_system = validate_system(system)

    found_access = check_access(username, system=normalized_system)
    systems_checked = 1 if normalized_system else len(available_systems)

    return AccessCheckResponse(
        username=username,
        systems_checked=systems_checked,
        access_found_count=len(found_access),
        access_found=found_access,
    )


@router.post("/users/{username}/grant/{system}", response_model=AccessActionResponse)
def grant_user_access(
    username: str,
    system: str,
    mock: bool = True,
    dry_run: bool = False,
) -> AccessActionResponse:
    """Grant access to a user for one system."""
    system_name = validate_system(system)

    grant_access(
        target_user=username,
        system=system_name,
        mock_mode=mock,
        dry_run=dry_run,
    )

    return AccessActionResponse(
        status="completed",
        username=username,
        system=system_name,
        action="grant",
        mock=mock,
        dry_run=dry_run,
    )


@router.post("/users/{username}/remove/{system}", response_model=AccessActionResponse)
def remove_user_access(
    username: str,
    system: str,
    mock: bool = True,
    dry_run: bool = False,
) -> AccessActionResponse:
    """Remove access from a user for one system."""
    system_name = validate_system(system)

    remove_access(
        target_user=username,
        system=system_name,
        mock_mode=mock,
        dry_run=dry_run,
    )

    return AccessActionResponse(
        status="completed",
        username=username,
        system=system_name,
        action="remove",
        mock=mock,
        dry_run=dry_run,
    )


@router.post("/tickets", response_model=TicketResponse, tags=["Tickets"])
def create_ticket(ticket_data: TicketCreate) -> TicketResponse:
    """Create a new ticket."""
    db = SessionLocal()

    try:
        ticket = Ticket(
            title=ticket_data.title,
            owner=ticket_data.owner,
            status=ticket_data.status,
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return ticket

    finally:
        db.close()


@router.get("/tickets", response_model=list[TicketResponse], tags=["Tickets"])
def get_tickets() -> list[TicketResponse]:
    """Return all tickets."""
    db = SessionLocal()

    try:
        return db.query(Ticket).all()

    finally:
        db.close()


@router.get("/tickets/{ticket_id}", response_model=TicketResponse, tags=["Tickets"])
def get_ticket(ticket_id: int) -> TicketResponse:
    """Return one ticket by ID."""
    db = SessionLocal()

    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise HTTPException(
                status_code=404,
                detail=f"Ticket not found: {ticket_id}",
            )

        return ticket

    finally:
        db.close()


@router.put("/tickets/{ticket_id}", response_model=TicketResponse, tags=["Tickets"])
def update_ticket(ticket_id: int, ticket_data: TicketUpdate) -> TicketResponse:
    """Update one ticket by ID."""
    db = SessionLocal()

    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise HTTPException(
                status_code=404,
                detail=f"Ticket not found: {ticket_id}",
            )

        if ticket_data.title is not None:
            ticket.title = ticket_data.title

        if ticket_data.owner is not None:
            ticket.owner = ticket_data.owner

        if ticket_data.status is not None:
            ticket.status = ticket_data.status

        db.commit()
        db.refresh(ticket)

        return ticket

    finally:
        db.close()


@router.delete("/tickets/{ticket_id}", tags=["Tickets"])
def delete_ticket(ticket_id: int) -> dict:
    """Delete one ticket by ID."""
    db = SessionLocal()

    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise HTTPException(
                status_code=404,
                detail=f"Ticket not found: {ticket_id}",
            )

        db.delete(ticket)
        db.commit()

        return {
            "status": "deleted",
            "ticket_id": ticket_id,
        }

    finally:
        db.close()


@router.get("/incidents", response_model=list[IncidentResponse], tags=["Incidents"])
def get_incidents() -> list[IncidentResponse]:
    """Return all incidents."""
    db = SessionLocal()

    try:
        return db.query(Incident).all()

    finally:
        db.close()


@router.get(
    "/access-requests",
    response_model=list[AccessRequestResponse],
    tags=["Access Requests"],
)
def get_access_requests() -> list[AccessRequestResponse]:
    """Return all access requests."""
    db = SessionLocal()

    try:
        return db.query(AccessRequest).all()

    finally:
        db.close()

@router.put("/access-requests/{request_id}/approve", tags=["Access Requests"])
def approve_access_request(request_id: int) -> dict:
    """Approve an access request."""
    db = SessionLocal()

    try:
        request = (
            db.query(AccessRequest)
            .filter(AccessRequest.id == request_id)
            .first()
        )

        if not request:
            raise HTTPException(
                status_code=404,
                detail=f"Request not found: {request_id}",
            )

        request.status = "approved"
        request.approved_by = "soc_admin"
        request.approved_at = datetime.utcnow()

        db.commit()

        return {
            "status": "approved",
            "request_id": request_id,
        }

    finally:
        db.close()


@router.put("/access-requests/{request_id}/complete", tags=["Access Requests"])
def complete_access_request(request_id: int) -> dict:
    """Complete an approved access request."""
    db = SessionLocal()

    try:
        request = (
            db.query(AccessRequest)
            .filter(AccessRequest.id == request_id)
            .first()
        )

        if not request:
            raise HTTPException(
                status_code=404,
                detail=f"Request not found: {request_id}",
            )

        request.status = "completed"
        request.completed_at = datetime.utcnow()

        db.commit()

        return {
            "status": "completed",
            "request_id": request_id,
        }

    finally:
        db.close()


def get_access_requests() -> list[dict]:
    """Return all access requests."""
    db = SessionLocal()

    try:
        requests = db.query(AccessRequest).all()

        return [
            {
                "id": req.id,
                "username": req.username,
                "system": req.system,
                "action": req.action,
                "status": req.status,
                "created_at": (
                    req.created_at.isoformat() if req.created_at else None
                ),
            }
            for req in requests
        ]

    finally:
        db.close()

@router.post("/alerts", response_model=AlertResponse, tags=["Alerts"])
def create_alert(alert_data: AlertCreate) -> AlertResponse:
    db = SessionLocal()

    try:
        alert = Alert(
            source=alert_data.source,
            severity=alert_data.severity,
            title=alert_data.title,
            description=alert_data.description,
            status=alert_data.status,
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    finally:
        db.close()


@router.get("/alerts", response_model=list[AlertResponse], tags=["Alerts"])
def get_alerts() -> list[AlertResponse]:
    db = SessionLocal()

    try:
        return db.query(Alert).all()

    finally:
        db.close()


@router.get("/alerts/{alert_id}", response_model=AlertResponse, tags=["Alerts"])
def get_alert(alert_id: int) -> AlertResponse:
    db = SessionLocal()

    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise HTTPException(
                status_code=404,
                detail=f"Alert not found: {alert_id}",
            )

        return alert

    finally:
        db.close()


@router.put("/alerts/{alert_id}", response_model=AlertResponse, tags=["Alerts"])
def update_alert(alert_id: int, alert_data: AlertUpdate) -> AlertResponse:
    db = SessionLocal()

    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise HTTPException(
                status_code=404,
                detail=f"Alert not found: {alert_id}",
            )

        if alert_data.source is not None:
            alert.source = alert_data.source
        if alert_data.severity is not None:
            alert.severity = alert_data.severity
        if alert_data.title is not None:
            alert.title = alert_data.title
        if alert_data.description is not None:
            alert.description = alert_data.description
        if alert_data.status is not None:
            alert.status = alert_data.status

        db.commit()
        db.refresh(alert)

        return alert

    finally:
        db.close()


@router.delete("/alerts/{alert_id}", tags=["Alerts"])
def delete_alert(alert_id: int) -> dict:
    db = SessionLocal()

    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise HTTPException(
                status_code=404,
                detail=f"Alert not found: {alert_id}",
            )

        db.delete(alert)
        db.commit()

        return {
            "status": "deleted",
            "alert_id": alert_id,
        }

    finally:
        db.close()