# app/models/application.py
from app.models.base import Base
from typing import Optional

class Application(Base):
    job_id: str
    user_id: str
    ats_resume_path: str
    status: str = "generated" # e.g., generated, applied
