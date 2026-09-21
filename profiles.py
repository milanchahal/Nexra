# backend/app/api/endpoints/profiles.py
import asyncio
import base64
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
import pypdf

from app.core.db import get_database, get_db_client
from app.services.profile_service import ProfileService
from app.models.profile import Profile
from app.models.user import User
from app.core.auth import get_current_user

router = APIRouter()

async def trigger_job_discovery(user_id: str):
    """Background task to trigger job discovery for a user."""
    from app.discovery.clawd_agent import ClawdJobDiscoveryAgent
    from app.core.db import get_db_client
    
    try:
        # Wait a bit for the profile to be fully saved
        await asyncio.sleep(2)
        
        client = get_db_client()
        agent = ClawdJobDiscoveryAgent(client)
        await agent.run_discovery_for_user(user_id)
    except Exception as e:
        print(f"Background discovery failed for user {user_id}: {e}")

@router.post("/resume", response_model=Profile, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Handles resume upload, text extraction, and profile creation/update.
    Stores original PDF bytes for in-place editing.
    Triggers job discovery in the background after profile creation.
    """
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")

    try:
        # Read the entire PDF file as bytes FIRST
        pdf_bytes = await file.read()
        
        # Store bytes as base64 string (for MongoDB storage)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Reset file pointer and extract text
        from io import BytesIO
        pdf_reader = pypdf.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        if not text or not text.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not extract any text from the PDF.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process PDF file: {e}")

    profile_service = ProfileService(db)
    profile = await profile_service.create_or_update_profile_from_resume(
        user_id=str(current_user.id),
        resume_text=text,
        original_filename=file.filename,
        pdf_base64=pdf_base64  # NEW: Store original PDF
    )
    
    # Trigger job discovery in the background
    background_tasks.add_task(trigger_job_discovery, str(current_user.id))
    
    return profile

@router.get("/me", response_model=Profile)
async def get_current_user_profile(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the full profile for the currently authenticated user.
    """
    profile_service = ProfileService(db)
    profile = await profile_service.get_profile(user_id=str(current_user.id))
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found for this user. Please upload a resume first.")
    return profile

@router.post("/build")
async def build_profile(
    background_tasks: BackgroundTasks,
    request: dict,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Finalizes the profile with job preferences and triggers job discovery.
    This marks the onboarding as complete.
    """
    profile_service = ProfileService(db)
    profile = await profile_service.get_profile(user_id=str(current_user.id))
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Profile not found. Please upload a resume first."
        )
    
    # Store preferences if provided
    preferences = request.get('preferences', {})
    
    # Trigger job discovery in the background
    background_tasks.add_task(trigger_job_discovery, str(current_user.id))
    
    return {
        "success": True,
        "message": "Profile built successfully! Job discovery has started.",
        "data": {
            "id": str(profile.id),
            "skills": profile.skills,
            "summary": profile.summary,
        }
    }

@router.post("/trigger-discovery")
async def manual_trigger_discovery(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger job discovery for the current user.
    Useful for refreshing job listings.
    """
    background_tasks.add_task(trigger_job_discovery, str(current_user.id))
    
    return {
        "success": True,
        "message": "Job discovery started! New jobs will appear in your dashboard shortly."
    }
