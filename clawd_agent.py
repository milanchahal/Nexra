# backend/app/discovery/clawd_agent.py
"""
Clawd.bot - The Job Discovery Agent
Automatically discovers jobs from multiple sources and matches them to user profiles.
Runs on a schedule and immediately when a new user completes onboarding.

Sources: 47 Remote Job Platforms (RemoteOK, Remotive, WeWorkRemotely, etc.)
         + GitHub Job Repos, Jobright, JobSpy, Company Career Pages
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# NEW: 47 Remote Job Platforms - Specialized Scrapers
from app.discovery.platforms import scrape_all_47_platforms

# Additional job sources
from app.discovery.dev_boards_scraper import scrape_dev_boards
from app.discovery.stealth_scraper import scrape_all_companies
from app.discovery.jobright_scraper import scrape_jobright
from app.discovery.github_jobs_scraper import scrape_github_jobs
from app.discovery.jobspy_scraper import scrape_jobspy_all
from app.discovery.deduplicator import filter_new_jobs, generate_dedupe_hash
from app.discovery.extractor import extract_job_details
from app.discovery.matcher import get_keywords_from_profile, calculate_match_score
from app.discovery.scorer import calculate_ats_score
from app.models.profile import Profile
from app.models.job import Job, JobStatus, OptimizedResume
from app.core.ai import ai_service
from bson import ObjectId

# Indian tech job queries - comprehensive list
TECH_JOB_QUERIES = [
    # Core Development
    "Software Engineer", "Software Developer", "Backend Developer", "Frontend Developer", 
    "Full Stack Developer", "Web Developer", "Application Developer",
    # Language Specific
    "Python Developer", "Java Developer", "JavaScript Developer", "React Developer",
    "Node.js Developer", "Angular Developer", "Vue.js Developer", "Django Developer",
    "Spring Boot Developer", "Go Developer", "Rust Developer", ".NET Developer",
    # Specialized
    "Data Scientist", "Data Analyst", "Data Engineer", "ML Engineer", "AI Engineer",
    "Machine Learning Engineer", "Deep Learning Engineer", "NLP Engineer",
    "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer", "Platform Engineer",
    "Mobile Developer", "Android Developer", "iOS Developer", "Flutter Developer",
    "React Native Developer", "QA Engineer", "Test Engineer", "Automation Engineer",
    # Entry Level / Intern
    "Software Internship", "Tech Internship", "Engineering Intern", "Developer Intern",
    "Data Science Internship", "ML Internship", "AI Internship", 
    "Graduate Engineer Trainee", "GET", "Fresher Software", "Entry Level Developer",
    "Associate Software Engineer", "Junior Developer", "Trainee Engineer",
]

# Indian locations to search
INDIAN_LOCATIONS = [
    "Bangalore", "Hyderabad", "Pune", "Chennai", "Mumbai", 
    "Delhi NCR", "Gurgaon", "Noida", "Kolkata", "Ahmedabad",
    "Remote India", "Work from Home"
]


class ClawdJobDiscoveryAgent:
    def __init__(self, db_client: AsyncIOMotorClient):
        from app.core.config import settings
        self.db: AsyncIOMotorDatabase = db_client[settings.MONGO_DATABASE_NAME]
        self.profiles_collection = self.db.get_collection("profiles")
        self.jobs_collection = self.db.get_collection("jobs")
        self.optimized_resumes_collection = self.db.get_collection("optimized_resumes")
        self.scheduler = AsyncIOScheduler()
        # Run every 2 hours for real-time discovery
        self.scheduler.add_job(self.run_discovery_for_all_users, 'interval', hours=2)
        # Keep-alive (Ping self every 14 mins to prevent Render spin-down)
        self.scheduler.add_job(self.keep_alive, 'interval', minutes=14)
        
        # Also run 5 minutes after startup
        self.scheduler.add_job(self.run_discovery_for_all_users, 'date', 
                              run_date=datetime.now().replace(microsecond=0))

    async def keep_alive(self):
        """Self-ping to keep Render free instance active."""
        from app.core.config import settings
        import httpx
        
        if not settings.RENDER_EXTERNAL_URL:
            return

        try:
            url = f"{settings.RENDER_EXTERNAL_URL}/"
            async with httpx.AsyncClient() as client:
                await client.get(url, timeout=10)
            print(f"   🔄 Keep-alive ping sent to {url}")
        except Exception as e:
            print(f"   ⚠️ Keep-alive ping failed: {e}")

    async def _auto_prepare_job_for_application(self, job_id: ObjectId, user_id: str):
        """
        Background task to auto-prepare a high-match job.
        Generates match explanation and optimized resume for jobs with score >= 80.
        """
        job_data = await self.jobs_collection.find_one({"_id": job_id})
        profile_data = await self.profiles_collection.find_one({"user_id": user_id})
        
        if not job_data or not profile_data:
            print(f"Could not find job or profile for auto-preparation. JobID: {job_id}")
            return

        job = Job(**job_data)
        profile = Profile(**profile_data)

        try:
            # 1. Generate 'Why you're a good match' explanation
            explanation = await ai_service.generate_match_explanation(
                profile_summary=profile.summary or "",
                profile_skills=profile.skills or [],
                job_title=job.job_title,
                job_description=job.job_description
            )
            
            # 2. Generate ATS-optimized resume
            optimized_resume_text = await ai_service.optimize_resume_for_job(
                original_resume_text=profile.raw_resume_text,
                job_description=job.job_description
            )
            
            ats_score = calculate_ats_score(optimized_resume_text, job.job_description, set(profile.skills or []))
            
            # 3. Save optimized resume
            optimized_resume = OptimizedResume(
                user_id=user_id,
                job_id=str(job_id),
                source_resume_version_id=profile.resume_versions[-1].version_id if profile.resume_versions else None,
                optimized_text=optimized_resume_text,
                ats_score=ats_score,
            )
            
            await self.optimized_resumes_collection.insert_one(optimized_resume.dict(by_alias=True))

            # 4. Update job with the new resume and explanation
            await self.jobs_collection.update_one(
                {"_id": job_id},
                {"$set": {
                    "match_explanation": explanation,
                    "active_optimized_resume_id": str(optimized_resume.id),
                    "status": JobStatus.RESUME_READY
                }}
            )
            
            print(f"✓ Auto-prepared job: {job.job_title} at {job.company_name} (Score: {job.match_score})")
            
        except Exception as e:
            print(f"✗ Failed to auto-prepare job {job_id}: {e}")

    async def run_discovery_cycle(self, user_id: str):
        """
        Runs a complete job discovery cycle for a single user.
        Scrapes all sources, deduplicates, scores, and auto-prepares high matches.
        """
        profile_data = await self.profiles_collection.find_one({"user_id": user_id})
        if not profile_data:
            print(f"User {user_id} has no profile. Skipping discovery.")
            return
            
        profile = Profile(**profile_data)
        user_keywords = get_keywords_from_profile(profile)
        
        print(f"\n🔍 Starting job discovery for user {user_id}")
        print(f"   Keywords: {user_keywords[:5]}...")

        # Get existing job hashes to avoid duplicates
        existing_hashes_cursor = self.jobs_collection.find({"user_id": user_id}, {"dedupe_hash": 1})
        existing_hashes = {doc["dedupe_hash"] async for doc in existing_hashes_cursor}

        # Select queries based on user's skills
        relevant_queries = []
        for query in TECH_JOB_QUERIES:
            if any(kw.lower() in query.lower() for kw in user_keywords[:10]):
                relevant_queries.append(query)
        # Add some default queries if we don't have enough
        if len(relevant_queries) < 5:
            relevant_queries.extend(TECH_JOB_QUERIES[:10])
        relevant_queries = list(set(relevant_queries))[:15]  # Limit to 15 queries

        all_scraped_jobs = []

        # ============================================================
        # 1. MAIN SOURCE: 47 Remote Job Platforms (NEW Specialized Scrapers)
        # ============================================================
        print("   🌍 Scraping 47 Remote Job Platforms (Specialized Scrapers)...")
        try:
            remote_jobs = await scrape_all_47_platforms(user_keywords)
            all_scraped_jobs.extend(remote_jobs)
            print(f"      Found {len(remote_jobs)} from 47 Remote Platforms")
        except Exception as e:
            print(f"      Remote Platforms error: {e}")

        # ============================================================
        # 2. Developer-specific Job Boards
        # ============================================================
        print("   📋 Scraping developer job boards...")
        try:
            dev_jobs = await scrape_dev_boards(user_keywords)
            all_scraped_jobs.extend(dev_jobs)
            print(f"      Found {len(dev_jobs)} from developer boards")
        except Exception as e:
            print(f"      Dev boards error: {e}")

        # ============================================================
        # 3. Company Career Pages (Stealth Mode)
        # ============================================================
        print("   📋 Scraping 200+ company career pages (stealth mode)...")
        try:
            career_jobs = await scrape_all_companies(user_keywords, max_companies=50)
            all_scraped_jobs.extend(career_jobs)
            print(f"      Found {len(career_jobs)} from company career pages")
        except Exception as e:
            print(f"      Career pages error: {e}")

        # ============================================================
        # 4. Jobright.ai - Premium Job Discovery
        # ============================================================
        print("   📋 Scraping Jobright.ai (Premium jobs)...")
        try:
            jobright_jobs = await scrape_jobright(user_keywords)
            all_scraped_jobs.extend(jobright_jobs)
            print(f"      Found {len(jobright_jobs)} from Jobright.ai")
        except Exception as e:
            print(f"      Jobright error: {e}")

        # ============================================================
        # 5. GitHub Job Repos (2026 Internship/New Grad lists)
        # ============================================================
        print("   📋 Scraping GitHub job repositories (curated lists)...")
        try:
            github_jobs = await scrape_github_jobs(user_keywords)
            all_scraped_jobs.extend(github_jobs)
            print(f"      Found {len(github_jobs)} from GitHub job repos")
        except Exception as e:
            print(f"      GitHub jobs error: {e}")

        # ============================================================
        # 6. JobSpy Aggregator (LinkedIn, Indeed, Glassdoor)
        # ============================================================
        print("   📋 Scraping via JobSpy aggregator...")
        try:
            jobspy_jobs = await scrape_jobspy_all(user_keywords)
            all_scraped_jobs.extend(jobspy_jobs)
            print(f"      Found {len(jobspy_jobs)} from JobSpy")
        except Exception as e:
            print(f"      JobSpy error: {e}")

        # Filter new jobs (remove duplicates)
        new_jobs_to_process = filter_new_jobs(all_scraped_jobs, existing_hashes)
        
        if not new_jobs_to_process:
            print(f"   No new jobs found for user {user_id}.\n")
            return

        print(f"   📊 Processing {len(new_jobs_to_process)} new unique jobs...")

        jobs_to_insert = []
        high_match_job_ids = []
        
        for job_data in new_jobs_to_process:
            # Calculate match score based on user's profile
            job_data['match_score'] = calculate_match_score(
                job_title=job_data.get('job_title', ''),
                job_description=job_data.get('job_description', ''),
                user_keywords=user_keywords
            )
            
            # Keep jobs with 20%+ match - show more jobs with any resemblance
            if job_data['match_score'] < 20:
                continue

            # Extract enhanced details (salary, mode, etc.) using AI
            # Only for decent matches (>40%) to save costs/time, or all? User wants "world class".
            # Let's do all > 20% but maybe async to not block loop too much.
            try:
                details = await extract_job_details(
                    job_data.get('job_description', ''), 
                    job_data.get('job_title', '')
                )
                if details:
                    # Only update fields that are not None (preserve existing data)
                    filtered_details = {k: v for k, v in details.items() if v is not None}
                    job_data.update(filtered_details)
                    print(f"      ✨ Extracted details for {job_data.get('job_title')[:20]}...")
            except Exception as e:
                print(f"      ⚠️ Extraction failed: {e}")
                
            job_data['user_id'] = user_id
            job_data['dedupe_hash'] = generate_dedupe_hash(
                job_data.get('job_title', ''), 
                job_data.get('company_name', '')
            )
            
            # Sanitize data to remove NaNs (pandas artifacts)
            for k, v in job_data.items():
                if isinstance(v, float) and (v != v):  # Check for NaN
                    job_data[k] = None

            try:
                job_model = Job(**job_data)
                jobs_to_insert.append(job_model.dict(by_alias=True))
                high_match_job_ids.append(job_model.id)
            except Exception as e:
                print(f"      ❌ Skipping job due to validation error: {e}")
                continue
        
        if jobs_to_insert:
            await self.jobs_collection.insert_many(jobs_to_insert)
            print(f"   ✅ Inserted {len(jobs_to_insert)} relevant jobs (20%+ match) for user {user_id}")
            print(f"   🎯 Auto-preparing top {min(5, len(high_match_job_ids))} jobs...")
            
            # Sort by match score and auto-prepare top 5
            # Jobs are already high-match, just prepare them
            for job_id in high_match_job_ids[:5]:
                asyncio.create_task(self._auto_prepare_job_for_application(job_id, user_id))
        else:
            print(f"   ⚠️ No jobs matched 80%+ threshold. Try broader keywords.")

    async def run_discovery_for_all_users(self):
        """
        Runs job discovery for all users with profiles.
        Called by the scheduler.
        """
        print("\n" + "="*60)
        print("🤖 CLAWD.BOT: Starting automated job discovery...")
        print("="*60)
        
        all_user_ids = await self.profiles_collection.distinct("user_id")
        print(f"Found {len(all_user_ids)} user(s) with profiles\n")
        
        for user_id in all_user_ids:
            try:
                await self.run_discovery_cycle(user_id)
            except Exception as e:
                print(f"Error in discovery for user {user_id}: {e}")
        
        print("\n" + "="*60)
        print("🤖 CLAWD.BOT: Discovery cycle complete!")
        print("="*60 + "\n")

    async def run_discovery_for_user(self, user_id: str):
        """
        Public method to trigger immediate discovery for a specific user.
        Called when a user completes onboarding.
        """
        print(f"\n🚀 Immediate discovery triggered for new user: {user_id}")
        await self.run_discovery_cycle(user_id)

    def start(self):
        """Starts the background scheduler."""
        print("🤖 Starting Clawd.bot Job Discovery Scheduler...")
        print("   - Running every 2 hours")
        print("   - Sources: 47 Remote Platforms, GitHub Jobs, Jobright, Company Pages")
        self.scheduler.start()

    def stop(self):
        """Stops the scheduler gracefully."""
        print("Shutting down Clawd.bot Job Discovery Scheduler...")
        self.scheduler.shutdown()


# Module-level agent instance for use by main.py
clawd_agent: ClawdJobDiscoveryAgent = None

def initialize_agent(db_client: AsyncIOMotorClient):
    """Initialize the global clawd agent instance."""
    global clawd_agent
    clawd_agent = ClawdJobDiscoveryAgent(db_client)
    clawd_agent.start()

def shutdown_agent():
    """Shutdown the global clawd agent."""
    global clawd_agent
    if clawd_agent:
        clawd_agent.stop()