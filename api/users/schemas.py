from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    display_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
