"""
Authentication Routes
POST /auth/register  — create new account
POST /auth/login     — get JWT token
GET  /auth/me        — current user info (protected)
POST /auth/logout    — client-side token disposal (stateless)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from models.database import User, get_db
from models.schemas import RegisterRequest, LoginRequest, TokenResponse, UserPublic
from services.auth_service import (
    hash_password, verify_password,
    create_access_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


from fastapi import HTTPException

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    try:
        password_hash = hash_password(req.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = User(
        username=req.username,
        email=req.email,
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})

    return TokenResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "email": user.email},
    )

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "email": user.email},
    )


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout():
    # JWT is stateless — instruct client to drop the token
    return {"message": "Logged out. Delete the token on the client side."}