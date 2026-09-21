# backend/app/models/job.py
from pydantic import Field, BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .base import MongoBaseModel, PyObjectId

class JobStatus(str, Enum):
    DISCOVERED = "discovered"
    RESUME_READY = "resume_ready"
    OPTIMIZED = "optimized"
    APPLIED = "applied"
    ARCHIVED = "archived"

class JobSource(str, Enum):
    # Traditional Job Boards
    LINKEDIN = "linkedin"
    NAUKRI = "naukri"
    COMPANY = "company"
    MANUAL = "manual"
    INTERNSHALA = "internshala"
    WELLFOUND = "wellfound"
    HIRECT = "hirect"
    DEVBOARD = "devboard"
    INDEED = "indeed"
    INSTAHYRE = "instahyre"
    COMPANY_CAREER = "company_career"
    JOBRIGHT = "jobright"
    GITHUB_JOBS = "github_jobs"
    GLASSDOOR = "glassdoor"
    
    # JobSpy aggregated sources
    JOBSPY = "jobspy"
    JOBSPY_LINKEDIN = "jobspy_linkedin"
    JOBSPY_INDEED = "jobspy_indeed"
    JOBSPY_GLASSDOOR = "jobspy_glassdoor"
    
    # Remote Job Platforms (47+ platforms)
    REMOTEOK = "remoteok"
    REMOTIVE = "remotive"
    WORKINGNOMADS = "workingnomads"
    HIMALAYAS = "himalayas"
    ARCDEV = "arcdev"
    WEWORKREMOTELY = "weworkremotely"
    FLEXJOBS = "flexjobs"
    JOBSPRESSO = "jobspresso"
    JUSTREMOTE = "justremote"
    JSREMOTELY = "jsremotely"
    HUBSTAFF = "hubstaff"
    NODESK = "nodesk"
    AUTHENTICJOBS = "authenticjobs"
    LANDINGJOBS = "landingjobs"
    TURING = "turing"
    PANGIAN = "pangian"
    POWERTOFLY = "powertofly"
    REMOTE100K = "remote100k"
    LEVELSFYI = "levelsfyi"
    WORKATASTARTUP = "workatastartup"
    FOURDAYWEEK = "4dayweek"
    SKIPTHEDRIVE = "skipthedrive"
    VANHACK = "vanhack"
    SNAPHUNT = "snaphunt"
    TOTALJOBS = "totaljobs"
    GUNIO = "gunio"
    HIRED = "hired"
    SOSHACE = "soshace"
    STRIDER = "strider"
    TECLA = "tecla"
    BEONTECH = "beontech"
    FLATWORLD = "flatworld"
    GEEKHUNTER = "geekhunter"
    IDEALIST = "idealist"
    KULA = "kula"
    LOKA = "loka"
    NIXA = "nixa"
    PROGRAMATHOR = "programathor"
    REMOTECOM = "remotecom"
    REMOTEYEAH = "remoteyeah"
    REVELO = "revelo"
    SEUJOB = "seujob"
    COODESH = "coodesh"
    IMPULSO = "impulso"
    INSQUAD = "insquad"
    DISTRO = "distro"
    
    # Internship Platforms
    UNSTOP = "unstop"
    REMOTIVE_INTERN = "remotive_intern"
    REMOTEOK_INTERN = "remoteok_intern"
    LINKEDIN_INTERN = "linkedin_intern"
    INDEED_INTERN = "indeed_intern"
    NAUKRI_INTERN = "naukri_intern"
    GLASSDOOR_INTERN = "glassdoor_intern"
    
    # Catch-all for any other sources
    OTHER = "other"

class ATSScore(BaseModel):
    """ A structured object for the ATS score breakdown. """
    score: int = 0
    skills_matched: int = 0
    total_skills_in_job: int = 0
    top_missing_skills: List[str] = []
    title_alignment: str = "low" # Can be 'low', 'medium', 'high'

class Job(MongoBaseModel):
    user_id: str = Field(..., index=True)
    job_title: str
    company_name: str
    job_description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source: JobSource = Field(default=JobSource.MANUAL)
    source_url: Optional[str] = None
    location: Optional[str] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    dedupe_hash: str = Field(..., index=True)
    match_score: int = Field(default=0, index=True)
    status: JobStatus = Field(default=JobStatus.DISCOVERED, index=True)
    match_explanation: Optional[str] = None
    active_optimized_resume_id: Optional[PyObjectId] = None
    
    # Enhanced job data fields
    salary_min: Optional[int] = None  # Minimum salary/stipend in INR
    salary_max: Optional[int] = None  # Maximum salary/stipend in INR
    salary_type: Optional[str] = None  # "monthly", "yearly", "hourly"
    work_mode: Optional[str] = None  # "remote", "onsite", "hybrid"
    duration: Optional[str] = None  # For internships: "3 months", "6 months"
    experience_required: Optional[str] = None  # "fresher", "1-2 years", etc.
    applied_at: Optional[datetime] = None  # When user marked as applied

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

class OptimizedResume(MongoBaseModel):
    user_id: str = Field(..., index=True)
    job_id: PyObjectId
    source_resume_version_id: PyObjectId
    optimized_text: str
    ats_score: ATSScore # Changed from int to the structured model
    refinement_instructions: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)
