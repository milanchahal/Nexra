# backend/app/api/endpoints/jobs.py
from fastapi import APIRouter, Depends, HTTPException, Body, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

# Try to import RateLimiter (may fail on some versions)
try:
    from fastapi_limiter.depends import RateLimiter
    HAS_RATE_LIMITER = True
except ImportError:
    HAS_RATE_LIMITER = False
    # Create a dummy dependency that does nothing
    def RateLimiter(*args, **kwargs):
        async def dummy():
            pass
        return dummy

from app.core.db import get_database
from app.services.job_service import JobService
from app.services.resume_service import ResumeService
from app.models.job import Job, OptimizedResume, JobStatus
from app.models.base import PyObjectId
from app.models.user import User
from app.core.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class JobCreateRequest(BaseModel):
    job_title: str
    company_name: str
    job_description: str

class ImproveResumeRequest(BaseModel):
    custom_instructions: str

# Corrected identifier for rate limiting using the authenticated user's ID
async def get_user_identifier(user: User = Depends(get_current_user)) -> str:
    return str(user.id)

# Rate limit for expensive AI operations - use compatible syntax
if HAS_RATE_LIMITER:
    try:
        # Try new syntax first (limit=, period=)
        ai_rate_limiter = RateLimiter(limit=10, period=3600, identifier=get_user_identifier)
    except TypeError:
        try:
            # Fall back to old syntax (times=, hours=)
            ai_rate_limiter = RateLimiter(times=10, hours=1, identifier=get_user_identifier)
        except TypeError:
            # If both fail, create a dummy
            async def ai_rate_limiter():
                pass
else:
    async def ai_rate_limiter():
        pass

@router.get("", response_model=List[Job], summary="Get All Dashboard Jobs")
async def get_dashboard_jobs(current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    service = JobService(db)
    return await service.get_jobs_for_dashboard(user_id=str(current_user.id))

@router.post("/manual", response_model=Job, status_code=status.HTTP_201_CREATED)
async def manual_create_job(request: JobCreateRequest, current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    service = JobService(db)
    return await service.create_job_manual(user_id=str(current_user.id), **request.dict())

@router.post("/{job_id}/mark-applied", response_model=Job, summary="Mark a Job as Applied")
async def mark_job_as_applied(job_id: PyObjectId, current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    service = JobService(db)
    updated_job = await service.update_job_status(job_id, str(current_user.id), JobStatus.APPLIED)
    if not updated_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return updated_job

@router.post("/{job_id}/mark-archived", response_model=Job, summary="Archive a Job")
async def mark_job_as_archived(job_id: PyObjectId, current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    """ Endpoint for the 'Ignore' button functionality. """
    service = JobService(db)
    updated_job = await service.update_job_status(job_id, str(current_user.id), JobStatus.ARCHIVED)
    if not updated_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return updated_job

class UpdateStatusRequest(BaseModel):
    status: str

@router.put("/{job_id}/status", response_model=Job, summary="Update Job Status")
async def update_job_status(job_id: PyObjectId, request: UpdateStatusRequest, current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    """ Generic endpoint to update job status (restore from archived, etc.) """
    service = JobService(db)
    try:
        job_status = JobStatus(request.status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {request.status}")
    updated_job = await service.update_job_status(job_id, str(current_user.id), job_status)
    if not updated_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return updated_job

@router.post("/{job_id}/optimize", response_model=OptimizedResume, summary="Optimize Resume for Job", dependencies=[Depends(ai_rate_limiter)])
async def optimize_resume_for_job(job_id: PyObjectId, current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    resume_service = ResumeService(db)
    optimized_resume = await resume_service.optimize_for_job(user_id=str(current_user.id), job_id=job_id)
    job_service = JobService(db)
    await job_service.update_job_status(job_id, str(current_user.id), JobStatus.OPTIMIZED)
    return optimized_resume

@router.post("/{job_id}/improve-resume", response_model=OptimizedResume, summary="Refine an optimized resume", dependencies=[Depends(ai_rate_limiter)])
async def improve_resume(job_id: PyObjectId, request: ImproveResumeRequest, current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    resume_service = ResumeService(db)
    refined_resume = await resume_service.refine_resume(user_id=str(current_user.id), job_id=job_id, custom_instructions=request.custom_instructions)
    if not refined_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not generate refined resume.")
    return refined_resume

@router.post("/seed-demo", summary="Add demo jobs for testing")
async def seed_demo_jobs(current_user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Adds sample demo jobs to the user's dashboard for testing purposes.
    """
    from app.discovery.deduplicator import generate_dedupe_hash
    import random
    
    demo_jobs = [
        {
            "job_title": "Senior Software Engineer",
            "company_name": "Google",
            "job_description": "Build scalable systems and lead technical initiatives. Experience with Python, Go, and distributed systems required.",
            "location": "Bangalore, India",
            "source": "linkedin",
            "source_url": "https://www.linkedin.com/jobs/view/example1",
            "match_score": random.randint(75, 95),
        },
        {
            "job_title": "Full Stack Developer",
            "company_name": "Microsoft",
            "job_description": "Develop cloud-based applications using React, Node.js, and Azure. Strong problem-solving skills needed.",
            "location": "Hyderabad, India",
            "source": "linkedin",
            "source_url": "https://www.linkedin.com/jobs/view/example2",
            "match_score": random.randint(70, 90),
        },
        {
            "job_title": "Backend Engineer",
            "company_name": "Amazon",
            "job_description": "Design and implement microservices. Experience with AWS, Java, and Python required.",
            "location": "Remote",
            "source": "naukri",
            "source_url": "https://www.naukri.com/job-listings/example3",
            "match_score": random.randint(65, 85),
        },
        {
            "job_title": "Python Developer",
            "company_name": "Flipkart",
            "job_description": "Build e-commerce platform features using Python and Django. FastAPI experience is a plus.",
            "location": "Bangalore, India",
            "source": "naukri",
            "source_url": "https://www.naukri.com/job-listings/example4",
            "match_score": random.randint(80, 95),
        },
        {
            "job_title": "React Developer",
            "company_name": "Swiggy",
            "job_description": "Create responsive UI components using React and TypeScript. Mobile-first design experience preferred.",
            "location": "Gurgaon, India",
            "source": "linkedin",
            "source_url": "https://www.linkedin.com/jobs/view/example5",
            "match_score": random.randint(60, 80),
        },
    ]
    
    service = JobService(db)
    jobs_collection = db.get_collection("jobs")
    user_id = str(current_user.id)
    
    inserted_count = 0
    for job_data in demo_jobs:
        job_data["user_id"] = user_id
        job_data["dedupe_hash"] = generate_dedupe_hash(job_data["job_title"], job_data["company_name"])
        job_data["status"] = JobStatus.DISCOVERED
        
        # Check if already exists
        existing = await jobs_collection.find_one({
            "user_id": user_id,
            "dedupe_hash": job_data["dedupe_hash"]
        })
        
        if not existing:
            job = Job(**job_data)
            await jobs_collection.insert_one(job.dict(by_alias=True))
            inserted_count += 1
    
    return {"message": f"Added {inserted_count} demo jobs to your dashboard", "total_demo_jobs": len(demo_jobs)}