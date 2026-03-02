"""
NexaDesk — Agentic AI IT Service Desk
======================================
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
Login: admin@nexadesk.com / Admin@123
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager
from loguru import logger
import sys, time, os

from config import settings
from database import init_db, SessionLocal
from routes import auth, tickets, analytics, kb

# ── Logging ──
os.makedirs("logs", exist_ok=True)
logger.remove()
logger.add(sys.stdout, colorize=True, level="DEBUG" if settings.debug else "INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <level>{message}</level>")
logger.add("logs/nexadesk.log", rotation="10 MB", retention="30 days", level="INFO")


# ── Startup ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    await _seed()
    logger.info("NexaDesk is ready!")
    logger.info(f"API Docs: http://localhost:{settings.port}/docs")
    yield
    logger.info("Shutting down gracefully...")


async def _seed():
    db = SessionLocal()
    try:
        from models.user import User, UserRole
        from models.kb_article import KBArticle
        from utils.security import hash_password
        from agents.resolver import KB_DATA

        if not db.query(User).filter(User.email == settings.admin_email).first():
            db.add(User(
                email=settings.admin_email, full_name=settings.admin_name,
                employee_id="ADMIN-001", department="IT Administration",
                hashed_password=hash_password(settings.admin_password),
                role=UserRole.ADMIN, is_active=True, is_verified=True,
            ))
            logger.info(f"Admin created: {settings.admin_email}")

        if db.query(KBArticle).count() == 0:
            for a in KB_DATA:
                db.add(KBArticle(
                    title=a["title"], description=a["description"],
                    category=a["category"], tags=",".join(a["tags"]),
                    resolution_steps=a["resolution"], icon=a["icon"],
                    success_count=a["similar_count"],
                    failure_count=int(a["similar_count"] * (1 - a["success_rate"])),
                ))
            logger.info(f"Seeded {len(KB_DATA)} KB articles")
        db.commit()
    except Exception as e:
        logger.error(f"Seed error: {e}")
        db.rollback()
    finally:
        db.close()


# ── App ──
app = FastAPI(
    title="NexaDesk API",
    description="Agentic AI IT Service Desk — 7 AI agents, JWT auth, full audit logging. Demo: admin@nexadesk.com / Admin@123",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"])

@app.middleware("http")
async def timing(request: Request, call_next):
    t = time.time()
    r = await call_next(request)
    r.headers["X-Process-Time"] = f"{time.time()-t:.4f}s"
    return r

@app.exception_handler(Exception)
async def global_error(request: Request, exc: Exception):
    logger.error(f"Unhandled: {exc} at {request.url.path}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(analytics.router)
app.include_router(kb.router)

# Serve frontend static files
_frontend = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(_frontend):
    app.mount("/app", StaticFiles(directory=_frontend, html=True), name="frontend")

@app.get("/", tags=["Health"])
def root():
    # If frontend exists, serve it directly
    _index = os.path.join(_frontend, "index.html")
    if os.path.exists(_index):
        return FileResponse(_index)
    return {"service": "NexaDesk API", "status": "operational",
            "version": settings.app_version, "docs": "/docs",
            "message": "NexaDesk Agentic AI Service Desk is running!"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "environment": settings.environment,
            "agents_online": 7}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
