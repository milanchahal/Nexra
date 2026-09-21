from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.core.auth import get_current_user
from app.models.user import User
from app.automation.browser import browser_manager
from app.automation.pdf_generator import generate_resume_pdf
from app.services.job_service import JobService
from app.services.profile_service import ProfileService
from app.core.db import get_database
from bson import ObjectId

router = APIRouter()

@router.post("/launch-apply/{job_id}")
async def launch_apply_flow(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Launches a visible browser for the user to apply to the job.
    This uses Playwright to open the browser and navigate to the job URL.
    Pre-fills form fields and attempts to attach the optimized resume.
    """
    job_service = JobService(db)
    profile_service = ProfileService(db)
    
    job = await job_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if not job.source_url:
        raise HTTPException(status_code=400, detail="Job has no source URL")

    # Get user profile for pre-fill data
    profile = await profile_service.get_profile(str(current_user.id))
    
    try:
        # Navigate to job page
        page = await browser_manager.navigate_to_job(job.source_url)
        
        # Prepare user data for form pre-fill
        user_data = {
            'name': profile.summary.split('\n')[0] if profile else '',  # Use first line of summary as name fallback
            'email': current_user.email,
        }
        
        # Attempt to pre-fill form fields (best effort)
        await browser_manager.prefill_form_fields(page, user_data)
        
        # If we have an optimized resume, generate PDF and try to attach
        if job.active_optimized_resume_id and profile:
            # Get the optimized resume text
            optimized_resumes_collection = db.get_collection("optimized_resumes")
            resume_data = await optimized_resumes_collection.find_one(
                {"_id": ObjectId(str(job.active_optimized_resume_id))}
            )
            
            if resume_data:
                # Generate PDF
                pdf_path = generate_resume_pdf(
                    resume_text=resume_data.get('optimized_text', profile.raw_resume_text),
                    user_id=str(current_user.id),
                    job_id=job_id
                )
                
                # Attempt to attach (best effort)
                await browser_manager.attach_resume(page, pdf_path)
        
        return {
            "message": f"Browser launched for job: {job.job_title}",
            "url": job.source_url,
            "prefill_attempted": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to launch browser: {str(e)}")
