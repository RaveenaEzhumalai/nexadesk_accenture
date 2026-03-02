"""User model"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone
import enum, uuid


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    AGENT = "agent"
    EMPLOYEE = "employee"


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    employee_id = Column(String, unique=True, index=True)
    department = Column(String, default="")
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.EMPLOYEE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    tickets = relationship("Ticket", back_populates="submitter", foreign_keys="Ticket.submitter_id")
