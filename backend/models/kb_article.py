"""Knowledge Base Article model"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from database import Base
from datetime import datetime, timezone
import uuid


class KBArticle(Base):
    __tablename__ = "kb_articles"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, nullable=False)
    tags = Column(String, default="")
    resolution_steps = Column(Text, default="")
    icon = Column(String, default="📄")
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
