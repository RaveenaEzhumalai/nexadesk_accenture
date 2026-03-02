"""Ticket routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone
import uuid, json

from database import get_db
from models.ticket import Ticket, TicketPriority, TicketStatus
from models.audit_log import AuditLog
from middleware.auth import get_current_user, get_optional_user
from models.user import User
from agents.orchestrator import orchestrator
from utils.security import sanitize_string
from loguru import logger

router = APIRouter(prefix="/tickets", tags=["Tickets"])


class TicketCreate(BaseModel):
    title: str
    description: str
    category: str = "Other"
    priority: str = "medium"
    submitter_name: str = ""
    submitter_email: str = ""
    employee_id: str = ""
    department: str = ""
    business_impact: str = ""


def make_ticket_number() -> str:
    from datetime import datetime
    return f"NDK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"


@router.post("/", status_code=201)
def create_ticket(data: TicketCreate, db: Session = Depends(get_db),
                  current_user: Optional[User] = Depends(get_optional_user)):
    # Sanitize inputs
    ticket_data = {
        "title": sanitize_string(data.title, 200),
        "description": sanitize_string(data.description, 5000),
        "category": sanitize_string(data.category, 100),
        "priority": data.priority if data.priority in ["low","medium","high","critical"] else "medium",
        "submitter_name": sanitize_string(data.submitter_name, 100),
        "submitter_email": sanitize_string(data.submitter_email, 200),
        "employee_id": sanitize_string(data.employee_id, 50),
        "department": sanitize_string(data.department, 100),
        "business_impact": sanitize_string(data.business_impact, 200),
    }
    if not ticket_data["title"] or not ticket_data["description"]:
        raise HTTPException(status_code=400, detail="Title and description are required")

    # Run agent pipeline
    outcome = orchestrator.process_ticket(ticket_data, db)

    # Save ticket
    ticket = Ticket(
        ticket_number=make_ticket_number(),
        title=ticket_data["title"],
        description=ticket_data["description"],
        category=ticket_data["category"],
        priority=TicketPriority(ticket_data["priority"]),
        status=TicketStatus.RESOLVED if outcome["status"] == "resolved" else TicketStatus.ESCALATED,
        submitter_id=current_user.id if current_user else None,
        submitter_name=ticket_data["submitter_name"],
        submitter_email=ticket_data["submitter_email"],
        employee_id=ticket_data["employee_id"],
        department=ticket_data["department"],
        business_impact=ticket_data["business_impact"],
        resolution_text=outcome["resolution_text"],
        assigned_to=outcome["assigned_to"],
        ai_resolution_confidence=outcome["confidence"],
        resolution_time_seconds=outcome["resolution_time_seconds"],
        sla_target_minutes=outcome["sla_target_minutes"],
        escalation_level=outcome.get("escalation_level") or "",
        escalation_reason=outcome.get("escalation_reason") or "",
        reasoning_trace=json.dumps(outcome.get("reasoning_trace", [])),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    logger.info(f"Ticket created: {ticket.ticket_number} — {outcome['status']}")
    return {
        "ticket_number": ticket.ticket_number,
        "ticket_id": ticket.id,
        "status": outcome["status"],
        "resolution_text": outcome["resolution_text"],
        "assigned_to": outcome["assigned_to"],
        "confidence": outcome["confidence"],
        "resolution_time_seconds": outcome["resolution_time_seconds"],
        "sla_target_minutes": outcome["sla_target_minutes"],
        "reasoning_trace": outcome.get("reasoning_trace", []),
        "created_at": ticket.created_at.isoformat(),
    }


@router.get("/")
def get_tickets(
    skip: int = 0, limit: int = 50,
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(Ticket)
    if status:
        q = q.filter(Ticket.status == status)
    if priority:
        q = q.filter(Ticket.priority == priority)
    tickets = q.order_by(desc(Ticket.created_at)).offset(skip).limit(limit).all()
    total = db.query(Ticket).count()
    return {
        "tickets": [{
            "id": t.id, "ticket_number": t.ticket_number, "title": t.title,
            "category": t.category, "priority": t.priority, "status": t.status,
            "submitter_name": t.submitter_name, "assigned_to": t.assigned_to,
            "ai_resolution_confidence": t.ai_resolution_confidence,
            "created_at": t.created_at.isoformat() if t.created_at else "",
        } for t in tickets],
        "total": total, "skip": skip, "limit": limit
    }


@router.get("/{ticket_id}")
def get_ticket(ticket_id: str, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(
        (Ticket.id == ticket_id) | (Ticket.ticket_number == ticket_id)
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {
        "id": ticket.id, "ticket_number": ticket.ticket_number,
        "title": ticket.title, "description": ticket.description,
        "category": ticket.category, "priority": ticket.priority,
        "status": ticket.status, "submitter_name": ticket.submitter_name,
        "submitter_email": ticket.submitter_email, "department": ticket.department,
        "resolution_text": ticket.resolution_text, "assigned_to": ticket.assigned_to,
        "ai_resolution_confidence": ticket.ai_resolution_confidence,
        "resolution_time_seconds": ticket.resolution_time_seconds,
        "reasoning_trace": json.loads(ticket.reasoning_trace or "[]"),
        "created_at": ticket.created_at.isoformat() if ticket.created_at else "",
    }
