# app/api/routers.py
from fastapi import APIRouter
from app.api.endpoints import profiles, jobs, discovery, auth, chat, ats

api_router = APIRouter()

# Auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# All profile-related endpoints, including resume upload and fetching the user profile
api_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])

# All job-related endpoints, including creating a job and optimizing a resume for it
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])

# Endpoint to manually trigger the job discovery agent
api_router.include_router(discovery.router, tags=["Discovery"])

# Automation/Browser endpoints
from app.api.endpoints import automation
api_router.include_router(automation.router, prefix="/automation", tags=["Automation"])

# AI Chat endpoint (Clawd chatbot)
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

# ATS Resume Optimization endpoints
api_router.include_router(ats.router, prefix="/ats", tags=["ATS"])