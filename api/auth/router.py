import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import User
from api.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from api.auth.security import get_password_hash, verify_password
from api.auth.jwt import create_access_token
from api.config import get_settings

logger = logging.getLogger(__name__)

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

@router.get("/google")
def google_login(request: Request):
    if not settings.google_client_id:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLIENT_ID is not configured."
        )
    
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    redirect_uri = f"{scheme}://{request.url.netloc}{settings.api_prefix}/auth/google/callback"
    
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        "scope=openid%20email%20profile&"
        "access_type=offline&"
        "prompt=select_account"
    )
    return RedirectResponse(google_auth_url)

@router.get("/google/callback")
def google_callback(
    request: Request,
    code: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db)
):
    if error:
        logger.error(f"Google login error redirect: {error}")
        return RedirectResponse(f"{settings.frontend_url}/login?error={error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")
        
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google client credentials are not configured.")
        
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    redirect_uri = f"{scheme}://{request.url.netloc}{settings.api_prefix}/auth/google/callback"
    
    # 1. Exchange auth code for access token and id_token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    
    try:
        with httpx.Client() as client:
            token_response = client.post(token_url, data=data)
            token_data = token_response.json()
            
        if "error" in token_data:
            logger.error(f"Google token exchange failed: {token_data}")
            return RedirectResponse(f"{settings.frontend_url}/login?error=token_exchange_failed")
            
        access_token = token_data.get("access_token")
        
        # 2. Get user info
        userinfo_url = f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={access_token}"
        with httpx.Client() as client:
            userinfo_response = client.get(userinfo_url)
            userinfo = userinfo_response.json()
            
        email = userinfo.get("email")
        google_id = userinfo.get("sub")
        display_name = userinfo.get("name")
        
        if not email:
            logger.error("Google userinfo missing email")
            return RedirectResponse(f"{settings.frontend_url}/login?error=email_not_provided")
            
        # 3. Check if user already exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Update google_id if not present
            if not user.google_id:
                user.google_id = google_id
                db.commit()
                db.refresh(user)
        else:
            # Create a new user with Google identity
            user = User(
                email=email,
                google_id=google_id,
                display_name=display_name,
                hashed_password=None  # No password for Google SSO users
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        # 4. Generate local JWT access token
        local_access_token = create_access_token(subject=user.id)
        
        # 5. Redirect back to frontend
        return RedirectResponse(f"{settings.frontend_url}/oauth-callback?token={local_access_token}")
        
    except Exception as e:
        logger.exception("Exception occurred during Google OAuth callback")
        return RedirectResponse(f"{settings.frontend_url}/login?error=internal_server_error")
