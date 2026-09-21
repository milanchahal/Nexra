# backend/app/services/resume_service.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException
from typing import Set

from app.models.job import Job, OptimizedResume, ATSScore
from app.models.profile import Profile
from app.core.ai import ai_service
from app.discovery.scorer import calculate_ats_score

class ResumeService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.profiles = db.get_collection("profiles")
        self.jobs = db.get_collection("jobs")
        self.optimized_resumes = db.get_collection("optimized_resumes")

    async def optimize_for_job(self, user_id: str, job_id: ObjectId) -> OptimizedResume:
        profile = await self._get_profile(user_id)
        job = await self._get_job(job_id, user_id)
        user_skills = set(profile.skills)

        optimized_text = await ai_service.optimize_resume_for_job(
            original_resume_text=profile.raw_resume_text,
            job_description=job.job_description
        )
        ats_score_obj = calculate_ats_score(optimized_text, job.job_description, user_skills)

        optimized_resume = OptimizedResume(
            user_id=user_id,
            job_id=job.id,
            source_resume_version_id=profile.active_resume_version_id,
            optimized_text=optimized_text,
            ats_score=ats_score_obj
        )
        await self.optimized_resumes.insert_one(optimized_resume.dict(by_alias=True))
        
        new_resume_data = await self.optimized_resumes.find_one({"_id": optimized_resume.id})
        return OptimizedResume(**new_resume_data)

    async def refine_resume(self, user_id: str, job_id: ObjectId, custom_instructions: str) -> OptimizedResume:
        profile = await self._get_profile(user_id)
        job = await self._get_job(job_id, user_id)
        user_skills = set(profile.skills)

        refined_text = await ai_service.optimize_resume_for_job(
            original_resume_text=profile.raw_resume_text,
            job_description=job.job_description,
            custom_instructions=custom_instructions
        )
        new_ats_score_obj = calculate_ats_score(refined_text, job.job_description, user_skills)

        refined_resume = OptimizedResume(
            user_id=user_id,
            job_id=job.id,
            source_resume_version_id=profile.active_resume_version_id,
            optimized_text=refined_text,
            ats_score=new_ats_score_obj,
            refinement_instructions=custom_instructions
        )
        insert_result = await self.optimized_resumes.insert_one(refined_resume.dict(by_alias=True))

        await self.jobs.update_one(
            {"_id": job.id},
            {"$set": {"active_optimized_resume_id": insert_result.inserted_id}}
        )

        new_resume_data = await self.optimized_resumes.find_one({"_id": refined_resume.id})
        return OptimizedResume(**new_resume_data)

    async def _get_profile(self, user_id: str) -> Profile:
        profile_data = await self.profiles.find_one({"user_id": user_id})
        if not profile_data:
            raise HTTPException(status_code=404, detail="Profile not found.")
        return Profile(**profile_data)

    async def _get_job(self, job_id: ObjectId, user_id: str) -> Job:
        job_data = await self.jobs.find_one({"_id": job_id, "user_id": user_id})
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found.")
        return Job(**job_data)