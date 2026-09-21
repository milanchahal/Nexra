# app/models/optimized_resume.py
"""
Model for storing optimized resumes per job
"""
from pydantic import Field, BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import MongoBaseModel, PyObjectId

class ATSScoreBreakdown(BaseModel):
    """Detailed ATS score breakdown"""
    overall_score: int = 0
    skills_match: int = 0
    experience_relevance: int = 0
    keyword_optimization: int = 0
    format_score: int = 0
    education_match: int = 0
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    matched_keywords: List[str] = []
    missing_keywords: List[str] = []
    recommendations: List[str] = []
    strengths: List[str] = []

class OptimizedResume(MongoBaseModel):
    """Optimized resume stored per job"""
    user_id: PyObjectId
    job_id: PyObjectId
    job_title: str
    company_name: str
    
    # Resume content
    original_resume_text: str
    optimized_resume_text: str
    
    # ATS Scores
    original_ats_score: ATSScoreBreakdown = Field(default_factory=ATSScoreBreakdown)
    optimized_ats_score: ATSScoreBreakdown = Field(default_factory=ATSScoreBreakdown)
    
    # Optimization details
    changes_made: List[str] = []
    keywords_added: List[str] = []
    optimization_summary: str = ""
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_downloaded: bool = False
    download_count: int = 0

class OptimizedResumeCreate(BaseModel):
    """Request model for creating optimized resume"""
    job_id: str
    
class OptimizedResumeResponse(BaseModel):
    """Response model for optimized resume"""
    id: str
    job_id: str
    job_title: str
    company_name: str
    original_ats_score: int
    optimized_ats_score: int
    score_improvement: int
    optimized_resume_preview: str  # First 500 chars
    changes_made: List[str]
    keywords_added: List[str]
    created_at: datetime
    
class ATSScoreResponse(BaseModel):
    """Response model for ATS score calculation"""
    overall_score: int
    skills_match: Dict[str, Any]
    experience_relevance: Dict[str, Any]
    keyword_optimization: Dict[str, Any]
    format_score: int
    education_match: int
    recommendations: List[str]
    strengths: List[str]
