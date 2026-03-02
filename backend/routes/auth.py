"""Auth routes — login and register"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models.user import User, UserRole
from models.audit_log import AuditLog
from utils.security import hash_password, verify_password, create_access_token, sanitize_string
from loguru import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    employee_id: str = ""
    department: str = ""


@router.post("/login")
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower(), User.is_active == True).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    log = AuditLog(user_id=user.id, user_email=user.email, action="LOGIN",
                   ip_address=request.client.host if request.client else "")
    db.add(log)
    db.commit()
    logger.info(f"Login: {user.email}")
    return {
        "access_token": token, "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name,
                 "role": user.role, "department": user.department}
    }


@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email.lower(),
        full_name=sanitize_string(data.full_name),
        employee_id=sanitize_string(data.employee_id) or f"EMP-{data.email.split('@')[0].upper()}",
        department=sanitize_string(data.department),
        hashed_password=hash_password(data.password),
        role=UserRole.EMPLOYEE,
        is_active=True, is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Registered: {user.email}")
    return {"message": "Account created successfully", "user_id": user.id}
