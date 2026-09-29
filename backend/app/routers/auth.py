from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import hashlib

from app.database import get_db
from app.models.user import User


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# =========================
# PASSWORD HASHING
# =========================

def hash_password(password: str) -> str:
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# =========================
# REQUEST MODELS
# =========================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# REGISTER
# =========================

@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    email = data.email.lower().strip()
    name = data.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Please enter your name."
        )

    if len(data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters long."
        )

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists."
        )

    # Create user
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(data.password),

        # Profile values will be completed later
        age=0,
        gender="not_set",
        height=0,
        weight=0,
        activity="not_set",
        goal="not_set"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Account created successfully",
        "user_id": user.id,
        "name": user.name,
        "email": user.email
    }


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    email = data.email.lower().strip()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if user.password_hash != hash_password(data.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "message": "Login successful",
        "user_id": user.id,
        "name": user.name,
        "email": user.email
    }