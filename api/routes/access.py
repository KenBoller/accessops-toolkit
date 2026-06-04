"""
AccessOps Toolkit - Access API Routes
-------------------------------------
REST endpoints for system discovery, access checks, grants, removals,
and platform summary stats.
"""

from pathlib import Path
import json
import sys

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.db import SessionLocal
from database.models import Ticket

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
    tickets_file = data_dir / "tickets.json"
    incidents_file = data_dir / "incidents.json"
    access_requests_file = data_dir / "access_requests.json"

    users_tracked = 0
    tickets_open = 0
    incidents_open = 0
    access_requests_pending = 0

    access_state = load_json_file(access_state_file, {})

    tracked_users = set()

    if isinstance(access_state, dict):
        for system_users in access_state.values():
            if isinstance(system_users, dict):
                tracked_users.update(system_users.keys())

    users_tracked = len(tracked_users)

    ticket_data = load_json_file(tickets_file, {})
    if isinstance(ticket_data, dict):
        tickets_open = sum(
            1
            for ticket in ticket_data.get("tickets", [])
            if ticket.get("status") == "open"
        )

    incident_data = load_json_file(incidents_file, {})
    if isinstance(incident_data, dict):
        incidents_open = sum(
            1
            for incident in incident_data.get("incidents", [])
            if incident.get("status") in {"open", "active", "triggered"}
        )

    request_data = load_json_file(access_requests_file, {})
    if isinstance(request_data, dict):
        access_requests_pending = sum(
            1
            for request in request_data.get("requests", [])
            if request.get("status") in {"pending", "pending_approval"}
        )

    return StatsResponse(
        systems_available=len(systems),
        users_tracked=users_tracked,
        tickets_open=tickets_open,
        incidents_open=incidents_open,
        access_requests_pending=access_requests_pending,
    )


@router.get("/users/{username}/access", response_model=AccessCheckResponse)
def get_user_access(username: str, system: str | None = None) -> AccessCheckResponse:
    """
    Check access for a user.

    Optional query parameter:
        ?system=jira
    """
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
    """
    Grant access to a user for one system.

    Defaults to mock mode for portfolio-safe API usage.
    """
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
    """
    Remove access from a user for one system.

    Defaults to mock mode for portfolio-safe API usage.
    """
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


@router.get("/tickets", tags=["Tickets"])
def get_tickets():

    db = SessionLocal()

    try:
        tickets = db.query(Ticket).all()

        return [
            {
                "id": ticket.id,
                "title": ticket.title,
                "owner": ticket.owner,
                "status": ticket.status,
            }
            for ticket in tickets
        ]

    finally:
        db.close()