from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import User
from api.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from api.auth.security import get_password_hash, verify_password
from api.auth.jwt import create_access_token
from api.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    new_user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        display_name=data.display_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(subject=new_user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
