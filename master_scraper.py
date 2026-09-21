# backend/app/discovery/platforms/master_scraper.py
"""
Master Scraper - Orchestrates all 47 platform scrapers + Internship Scrapers
This file combines results from all scraper modules with proper error handling.
"""
import asyncio
from typing import List, Dict
from datetime import datetime

# Import all scraper modules
from .api_scrapers import scrape_all_api_platforms
from .rss_scrapers import scrape_all_rss_platforms
from .web_scrapers import scrape_all_web_platforms
from .latam_scrapers import scrape_all_latam_platforms
from .premium_scrapers import scrape_all_premium_platforms
from .internship_scrapers import scrape_all_internships


async def scrape_all_47_platforms(user_keywords: List[str] = None) -> List[Dict]:
    """
    Master function that runs all 47 platform scrapers.
    
    Args:
        user_keywords: Optional list of keywords to filter jobs (based on user's resume)
    
    Returns:
        List of job dictionaries from all platforms
    """
    print("\n" + "="*60)
    print("🚀 STARTING 47 PLATFORM SCRAPER")
    print("="*60)
    
    start_time = datetime.now()
    all_jobs = []
    
    # Run all scraper categories
    try:
        # Tier 1: API-based scrapers (most reliable)
        api_jobs = await scrape_all_api_platforms()
        all_jobs.extend(api_jobs)
    except Exception as e:
        print(f"   ⚠️ API scrapers error: {str(e)[:50]}")
    
    try:
        # Tier 1.5: RSS-based scrapers (very reliable)
        rss_jobs = await scrape_all_rss_platforms()
        all_jobs.extend(rss_jobs)
    except Exception as e:
        print(f"   ⚠️ RSS scrapers error: {str(e)[:50]}")
    
    await asyncio.sleep(0.5)  # Brief pause between tiers
    
    try:
        # Tier 2: Web scrapers
        web_jobs = await scrape_all_web_platforms()
        all_jobs.extend(web_jobs)
    except Exception as e:
        print(f"   ⚠️ Web scrapers error: {str(e)[:50]}")
    
    await asyncio.sleep(0.5)
    
    try:
        # Tier 2.5: LATAM scrapers
        latam_jobs = await scrape_all_latam_platforms()
        all_jobs.extend(latam_jobs)
    except Exception as e:
        print(f"   ⚠️ LATAM scrapers error: {str(e)[:50]}")
    
    await asyncio.sleep(0.5)
    
    try:
        # Tier 3: Premium scrapers
        premium_jobs = await scrape_all_premium_platforms()
        all_jobs.extend(premium_jobs)
    except Exception as e:
        print(f"   ⚠️ Premium scrapers error: {str(e)[:50]}")
    
    await asyncio.sleep(0.5)
    
    try:
        # Tier 4: INTERNSHIPS (for students like DTU, IIT, NIT)
        print("   🎓 Scraping internship platforms...")
        internship_jobs = await scrape_all_internships()
        all_jobs.extend(internship_jobs)
    except Exception as e:
        print(f"   ⚠️ Internship scrapers error: {str(e)[:50]}")
    
    # Filter by user keywords if provided
    if user_keywords and len(user_keywords) > 0:
        filtered_jobs = []
        keywords_lower = [kw.lower() for kw in user_keywords]
        
        for job in all_jobs:
            job_text = f"{job.get('job_title', '')} {job.get('job_description', '')} {job.get('company_name', '')}".lower()
            
            # Check if any keyword matches
            if any(kw in job_text for kw in keywords_lower):
                filtered_jobs.append(job)
        
        print(f"   🎯 Filtered to {len(filtered_jobs)} jobs matching keywords")
        all_jobs = filtered_jobs
    
    # Deduplicate by title + company
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job.get('job_title', '').lower()}_{job.get('company_name', '').lower()}"
        if key not in seen and len(job.get('job_title', '')) > 3:
            seen.add(key)
            unique_jobs.append(job)
    
    # Calculate stats
    elapsed = (datetime.now() - start_time).total_seconds()
    sources = {}
    for job in unique_jobs:
        src = job.get('source', 'unknown')
        sources[src] = sources.get(src, 0) + 1
    
    print("\n" + "="*60)
    print(f"✅ SCRAPING COMPLETE: {len(unique_jobs)} unique jobs in {elapsed:.1f}s")
    print("="*60)
    print("📊 Jobs by source:")
    for src, count in sorted(sources.items(), key=lambda x: -x[1])[:20]:
        print(f"   • {src}: {count}")
    print("="*60 + "\n")
    
    return unique_jobs


async def scrape_top_platforms_only() -> List[Dict]:
    """
    Scrape only the most reliable platforms (API + RSS).
    Use this for quick scraping when you need results fast.
    """
    print("\n⚡ Quick scrape: API + RSS platforms only...")
    
    results = await asyncio.gather(
        scrape_all_api_platforms(),
        scrape_all_rss_platforms(),
        return_exceptions=True
    )
    
    all_jobs = []
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job.get('job_title', '').lower()}_{job.get('company_name', '').lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    print(f"   ✅ Quick scrape complete: {len(unique_jobs)} jobs")
    return unique_jobs


# For direct testing
if __name__ == "__main__":
    # Test with user's resume keywords
    user_keywords = [
        "python", "javascript", "typescript", "react", "node",
        "software engineer", "developer", "intern", "full stack",
        "backend", "frontend", "machine learning", "ml", "ai"
    ]
    
    jobs = asyncio.run(scrape_all_47_platforms(user_keywords))
    
    print(f"\n🎯 Total matching jobs: {len(jobs)}")
    for j in jobs[:10]:
        print(f"   • {j['job_title'][:50]} @ {j['company_name']} ({j['source']})")
