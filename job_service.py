# backend/app/services/job_service.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.job import Job, JobStatus
from bson import ObjectId
from typing import List
from pymongo import DESCENDING

class JobService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.get_collection("jobs")

    async def create_job_manual(self, user_id: str, job_title: str, company_name: str, job_description: str) -> Job:
        """ Creates a job added manually by the user. """
        from app.discovery.deduplicator import generate_dedupe_hash
        
        job = Job(
            user_id=user_id,
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            dedupe_hash=generate_dedupe_hash(job_title, company_name),
            status=JobStatus.DISCOVERED # Or another default status for manual adds
        )
        await self.collection.insert_one(job.dict(by_alias=True))
        
        new_job_data = await self.collection.find_one({"_id": job.id})
        return Job(**new_job_data)

    async def get_jobs_for_dashboard(self, user_id: str) -> List[Job]:
        """
        Gets all non-archived jobs for a user's dashboard.
        Returns jobs with 20%+ match score, sorted by match score (highest first).
        """
        cursor = self.collection.find({
            "user_id": user_id,
            "status": {"$ne": JobStatus.ARCHIVED}
            # Remove match_score filter completely to show ALL jobs
        }).sort([
            ("match_score", DESCENDING),  # Highest match first
            ("discovered_at", DESCENDING)
        ]).limit(500)  # Increase limit to 500
        
        jobs = await cursor.to_list(length=500)
        return [Job(**job_data) for job_data in jobs]

    async def update_job_status(self, job_id: ObjectId, user_id: str, new_status: JobStatus) -> Job | None:
        """ Updates the status of a specific job. Locks resume reference when applied. """
        from datetime import datetime
        
        update_data = {"status": new_status}
        
        # If marking as applied, record the timestamp and lock the resume
        if new_status == JobStatus.APPLIED:
            update_data["applied_at"] = datetime.utcnow()
            # The active_optimized_resume_id is already set, this just ensures we don't change it
        
        await self.collection.update_one(
            {"_id": job_id, "user_id": user_id},
            {"$set": update_data}
        )
        
        updated_job_data = await self.collection.find_one({"_id": job_id, "user_id": user_id})
        return Job(**updated_job_data) if updated_job_data else None

    async def get_job(self, job_id: str | ObjectId) -> Job | None:
        if isinstance(job_id, str):
            try:
                job_id = ObjectId(job_id)
            except:
                return None
                
        job_data = await self.collection.find_one({"_id": job_id})
        if job_data:
            return Job(**job_data)
        return None
