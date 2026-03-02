"""NexaDesk — Database Setup (SQLite for dev, PostgreSQL for prod)"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings
from loguru import logger

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    from models import user, ticket, kb_article, audit_log
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
