"""Ticket model"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Enum as SAEnum, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import enum, uuid


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TicketCategory(str, enum.Enum):
    NETWORK = "Network / VPN"
    EMAIL = "Email / Outlook"
    HARDWARE = "Laptop / Hardware"
    SOFTWARE = "Software / Application"
    ACCESS = "Access / Permissions"
    SECURITY = "Security / Phishing"
    DATA = "Data Loss"
    SERVER = "Server / Infrastructure"
    OTHER = "Other"


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_number = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, default="Other")
    priority = Column(SAEnum(TicketPriority), default=TicketPriority.MEDIUM)
    status = Column(SAEnum(TicketStatus), default=TicketStatus.OPEN)
    submitter_id = Column(String, ForeignKey("users.id"), nullable=True)
    submitter_name = Column(String, default="")
    submitter_email = Column(String, default="")
    employee_id = Column(String, default="")
    department = Column(String, default="")
    business_impact = Column(String, default="")
    resolution_text = Column(Text, default="")
    assigned_to = Column(String, default="")
    ai_resolution_confidence = Column(Float, default=0.0)
    resolution_time_seconds = Column(Float, default=0.0)
    sla_target_minutes = Column(Integer, default=240)
    escalation_level = Column(String, default="")
    escalation_reason = Column(String, default="")
    reasoning_trace = Column(Text, default="[]")
    user_rating = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    submitter = relationship("User", back_populates="tickets", foreign_keys=[submitter_id])
