# backend/app/models/profile.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from .base import MongoBaseModel, PyObjectId

# --- Sub-documents ---

class ResumeVersion(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    version_id: PyObjectId = Field(default_factory=ObjectId)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: str
    source_file_name: Optional[str] = None

class Experience(BaseModel):
    role: str
    company: str
    duration: str
    bullet_points: List[str]

class Education(BaseModel):
    degree: str
    institution: str
    graduation_year: Optional[str] = None

# --- Main Profile Document ---

class Profile(MongoBaseModel):
    user_id: str = Field(..., index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # The original, unmodified resume text. This is our source of truth.
    raw_resume_text: str 
    
    # Original PDF stored as base64 for in-place editing
    original_pdf_base64: Optional[str] = None
    
    # The most recent resume version ID used to generate the raw_resume_text
    active_resume_version_id: PyObjectId

    # Structured data extracted by AI
    summary: str
    skills: List[str]
    experiences: List[Experience]
    educations: List[Education]
    
    # History of all resume uploads
    resume_versions: List[ResumeVersion] = []

    # Note: model_config is inherited from MongoBaseModel


class ProfileCreate(BaseModel):
    """Pydantic model for AI validation"""
    summary: str
    skills: List[str]
    experiences: List[Experience]
    educations: List[Education]