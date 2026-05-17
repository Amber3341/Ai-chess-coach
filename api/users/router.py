from fastapi import APIRouter, Depends
from api.models import User
from api.auth.dependencies import get_current_user
from api.users.schemas import UserProfile

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
