"""
AccessOps Toolkit - Database Models
-----------------------------------
SQLAlchemy ORM models for AccessOps Toolkit.

These models represent database-backed operational objects used by the
FastAPI layer.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Ticket(Base):
    """Support or operations ticket."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)


class Incident(Base):
    """Operational incident or alert-driven event."""

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    severity = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Investigating")
    created_at = Column(DateTime, default=datetime.utcnow)


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, nullable=False)
    system = Column(String, nullable=False)

    action = Column(String, nullable=False)

    status = Column(String, nullable=False, default="pending")

    requested_by = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)

    rt_ticket = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

class Alert(Base):
    """SOC alert or monitoring event."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="Medium")
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)