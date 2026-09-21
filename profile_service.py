# backend/app/services/profile_service.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.profile import Profile, ResumeVersion
from app.core.ai import ai_service
from datetime import datetime
from bson import ObjectId
from typing import Optional

class ProfileService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db.get_collection("profiles")

    async def get_profile(self, user_id: str) -> Profile | None:
        profile_data = await self.db.find_one({"user_id": user_id})
        return Profile(**profile_data) if profile_data else None

    async def create_or_update_profile_from_resume(
        self, user_id: str, resume_text: str, original_filename: str,
        pdf_base64: Optional[str] = None
    ) -> Profile:
        
        # Use AI to extract structured data
        structured_data = await ai_service.extract_profile_from_text(resume_text)
        
        new_version = ResumeVersion(
            notes="Initial resume upload.",
            source_file_name=original_filename,
        )

        existing_profile_data = await self.db.find_one({"user_id": user_id})

        if existing_profile_data:
            # User is uploading a new resume, create a new version and update profile
            existing_profile = Profile(**existing_profile_data)
            existing_profile.resume_versions.append(new_version)
            
            update_data = {
                "raw_resume_text": resume_text,
                "active_resume_version_id": new_version.version_id,
                "summary": structured_data.summary,
                "skills": structured_data.skills,
                "experiences": [exp.dict() for exp in structured_data.experiences],
                "educations": [edu.dict() for edu in structured_data.educations],
                "resume_versions": [v.dict() for v in existing_profile.resume_versions],
                "updated_at": datetime.utcnow(),
            }
            
            # Store original PDF if provided
            if pdf_base64:
                update_data["original_pdf_base64"] = pdf_base64
            
            await self.db.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
        else:
            # First time user, create a new profile
            new_profile = Profile(
                user_id=user_id,
                raw_resume_text=resume_text,
                active_resume_version_id=new_version.version_id,
                resume_versions=[new_version],
                **structured_data.dict()
            )
            profile_dict = new_profile.dict(by_alias=True)
            
            # Store original PDF if provided
            if pdf_base64:
                profile_dict["original_pdf_base64"] = pdf_base64
            
            await self.db.insert_one(profile_dict)
        
        # Return the latest state of the profile
        latest_profile_data = await self.db.find_one({"user_id": user_id})
        return Profile(**latest_profile_data)