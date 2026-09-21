# backend/app/models/user.py
from datetime import datetime
from pydantic import Field, EmailStr, ConfigDict
from .base import MongoBaseModel

class User(MongoBaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    email: EmailStr = Field(..., index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)