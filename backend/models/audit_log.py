"""Audit Log model — immutable compliance log"""
from sqlalchemy import Column, String, DateTime, Text
from database import Base
from datetime import datetime, timezone
import uuid


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    action = Column(String, nullable=False)
    resource = Column(String, default="")
    resource_id = Column(String, default="")
    details = Column(Text, default="{}")
    ip_address = Column(String, default="")
    user_agent = Column(String, default="")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
