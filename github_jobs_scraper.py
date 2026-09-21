"""
GitHub Job Repos Scraper
Fetches curated job listings from popular GitHub repositories
that maintain updated lists of internships and new grad positions.
"""
import asyncio
import httpx
import json
import re
from typing import List, Dict
from datetime import datetime

# GitHub API Base URL
GITHUB_API = "https://api.github.com"
GITHUB_RAW = "https://raw.githubusercontent.com"

# Curated GitHub repos with job data
# Format: (owner, repo, data_file_path, job_type)
JOB_REPOS = [
    # 2026 Software Engineer Jobs (316 jobs!)
    ("jobright-ai", "2026-Software-Engineer-New-Grad", "README.md", "new_grad"),
    ("jobright-ai", "2026-Software-Engineer-Internship", "README.md", "internship"),
    
    # Data Analysis (130+ jobs)
    ("jobright-ai", "2026-Data-Analysis-New-Grad", "README.md", "new_grad"),
    ("jobright-ai", "2026-Data-Analysis-Internship", "README.md", "internship"),
    
    # Product Management (92+ jobs)
    ("jobright-ai", "2026-Product-Management-New-Grad", "README.md", "new_grad"),
    ("jobright-ai", "2026-Product-Management-Internship", "README.md", "internship"),
    
    # Engineering & Development
    ("jobright-ai", "2026-Engineering-New-Grad", "README.md", "new_grad"),
    ("jobright-ai", "2026-Engineer-Internship", "README.md", "internship"),
    
    # Design
    ("jobright-ai", "2026-Design-New-Grad", "README.md", "new_grad"),
    ("jobright-ai", "2026-Design-Internship", "README.md", "internship"),
    
    # Business Analyst
    ("jobright-ai", "2026-Business-Analyst-New-Grad", "README.md", "new_grad"),
    ("jobright-ai", "2026-Business-Analyst-Internship", "README.md", "internship"),
    
    # H1B Sponsorship Jobs (261 jobs!)
    ("jobright-ai", "Daily-H1B-Jobs-In-Tech", "README.md", "h1b_sponsor"),
]

# Alternative popular repos
ALTERNATIVE_REPOS = [
    # SimplifyJobs maintained repos
    ("SimplifyJobs", "Summer2025-Internships", "README.md", "internship"),
    ("SimplifyJobs", "New-Grad-Positions", "README.md", "new_grad"),
    
    # Pitt CSC maintained
    ("pittcsc", "Summer2025-Internships", "README.md", "internship"),
]

def get_headers():
    """Get GitHub API headers"""
    return {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Job-Discovery-Bot/1.0",
    }

async def fetch_readme_content(owner: str, repo: str, file_path: str = "README.md") -> str:
    """Fetch README content from GitHub repo"""
    url = f"{GITHUB_RAW}/{owner}/{repo}/main/{file_path}"
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=get_headers())
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                # Try master branch
                url = f"{GITHUB_RAW}/{owner}/{repo}/master/{file_path}"
                response = await client.get(url, headers=get_headers())
                if response.status_code == 200:
                    return response.text
    except Exception as e:
        print(f"      Error fetching {owner}/{repo}: {e}")
    
    return ""

def parse_markdown_table(content: str) -> List[Dict]:
    """Parse markdown table into list of jobs"""
    jobs = []
    
    # Find all tables (lines starting with |)
    lines = content.split('\n')
    in_table = False
    headers = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('|') and line.endswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            
            if not in_table:
                # This is the header row
                headers = [h.lower().replace(' ', '_') for h in cells]
                in_table = True
            elif all(c.replace('-', '').replace(':', '') == '' for c in cells):
                # This is the separator row (|---|---|)
                continue
            else:
                # This is a data row
                job = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        job[headers[i]] = cell
                
                if job:
                    jobs.append(job)
        else:
            in_table = False
            headers = []
    
    return jobs

def extract_links(text: str) -> Dict[str, str]:
    """Extract markdown links from text"""
    links = {}
    # Match [text](url) pattern
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, text)
    for name, url in matches:
        links[name] = url
    return links

def normalize_job(raw_job: Dict, job_type: str, source_repo: str) -> Dict:
    """Normalize scraped job to our standard format"""
    # Try to find company name
    company = raw_job.get('company', '')
    if not company:
        company = raw_job.get('company_name', '')
    if not company:
        # Try to extract from first column
        first_col = list(raw_job.values())[0] if raw_job else ''
        links = extract_links(str(first_col))
        if links:
            company = list(links.keys())[0]
    
    # Try to find job title/role
    title = raw_job.get('role', '')
    if not title:
        title = raw_job.get('position', '')
    if not title:
        title = raw_job.get('title', '')
    if not title:
        # Extract from role column
        role_col = raw_job.get('role', '') or raw_job.get('roles', '')
        links = extract_links(str(role_col))
        if links:
            title = list(links.keys())[0]
    
    # Extract location
    location = raw_job.get('location', '')
    if not location:
        location = raw_job.get('locations', '')
    
    # Extract apply link
    apply_link = ""
    for col_name, col_value in raw_job.items():
        if 'apply' in col_name.lower() or 'link' in col_name.lower():
            links = extract_links(str(col_value))
            if links:
                apply_link = list(links.values())[0]
                break
    
    # If no direct apply link, try role column
    if not apply_link:
        for col_value in raw_job.values():
            links = extract_links(str(col_value))
            for link_url in links.values():
                if 'apply' in link_url.lower() or 'careers' in link_url.lower() or 'jobs' in link_url.lower():
                    apply_link = link_url
                    break
    
    # Extract posted date
    posted_date = raw_job.get('date_posted', '')
    if not posted_date:
        posted_date = raw_job.get('date', '')
    
    return {
        "job_title": title or "Software Engineer",
        "company_name": company.replace('**', '').strip() or "Unknown",
        "location": location.replace('</br>', ', ').strip() or "Remote / USA",
        "job_description": f"{job_type.replace('_', ' ').title()} position. Source: {source_repo}",
        "source": "github_jobs",
        "source_url": apply_link or f"https://github.com/{source_repo}",
        "posted_date": posted_date or str(datetime.now().date()),
        "job_type": job_type,
        "salary_range": raw_job.get('salary', '') or "",
        "experience_level": "Entry Level" if job_type in ['internship', 'new_grad'] else "",
    }

async def scrape_github_repo(owner: str, repo: str, file_path: str, job_type: str) -> List[Dict]:
    """Scrape jobs from a single GitHub repo"""
    jobs = []
    
    content = await fetch_readme_content(owner, repo, file_path)
    if not content:
        return jobs
    
    # Parse markdown tables
    raw_jobs = parse_markdown_table(content)
    
    # Normalize each job
    for raw_job in raw_jobs[:50]:  # Limit to 50 per repo
        try:
            job = normalize_job(raw_job, job_type, f"{owner}/{repo}")
            if job['company_name'] != "Unknown":
                jobs.append(job)
        except Exception:
            continue
    
    return jobs

async def scrape_github_jobs(user_keywords: List[str] = None) -> List[Dict]:
    """
    Main function to scrape all GitHub job repos
    Returns list of jobs in our standard format
    """
    all_jobs = []
    
    print("   🔍 Fetching from GitHub job repositories...")
    
    # Filter repos based on user keywords if provided
    repos_to_scrape = JOB_REPOS.copy()
    
    # Add alternative repos
    repos_to_scrape.extend(ALTERNATIVE_REPOS)
    
    # Scrape each repo
    for owner, repo, file_path, job_type in repos_to_scrape[:8]:  # Limit to 8 repos
        try:
            jobs = await scrape_github_repo(owner, repo, file_path, job_type)
            all_jobs.extend(jobs)
            print(f"      ✓ {owner}/{repo}: {len(jobs)} jobs")
            await asyncio.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"      ✗ {owner}/{repo}: {str(e)[:30]}")
    
    # Filter by user keywords if provided
    if user_keywords:
        keyword_set = set(kw.lower() for kw in user_keywords)
        filtered_jobs = []
        for job in all_jobs:
            job_text = f"{job['job_title']} {job['company_name']} {job['job_description']}".lower()
            if any(kw in job_text for kw in keyword_set):
                filtered_jobs.append(job)
        if filtered_jobs:
            all_jobs = filtered_jobs
    
    # Deduplicate by title + company
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['job_title']}_{job['company_name']}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    print(f"   ✅ Found {len(unique_jobs)} unique jobs from GitHub repos")
    return unique_jobs

# For testing
if __name__ == "__main__":
    async def test():
        jobs = await scrape_github_jobs(["software engineer", "react", "python"])
        print(f"\nTotal: {len(jobs)} jobs")
        for job in jobs[:5]:
            print(f"  - {job['job_title']} at {job['company_name']}")
    
    asyncio.run(test())
