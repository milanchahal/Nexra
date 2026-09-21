import hashlib
import re
from typing import List, Dict, Set

def generate_dedupe_hash(job_title: str, company_name: str) -> str:
    """
    Creates a unique and consistent hash for a job based on its title and company.
    Normalizes inputs to ensure "Google" and "google" produce the same hash.
    Also handles internal whitespace variants.
    """
    # Normalize by lowercasing, stripping, and collapsing internal whitespace
    def normalize(s):
        if s is None:
            return ""
        s = str(s).lower().strip()
        return re.sub(r'\s+', ' ', s)

    norm_title = normalize(job_title)
    norm_company = normalize(company_name)
    
    # Create a stable string to hash
    unique_string = f"{norm_company}-{norm_title}"
    
    return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

def filter_new_jobs(jobs: List[Dict], existing_hashes: Set[str]) -> List[Dict]:
    """
    Filters a list of scraped jobs, returning only those not present in the
    set of existing hashes. It also adds the new dedupe_hash to each new job.
    
    Args:
        jobs: A list of job dictionaries scraped from a source.
        existing_hashes: A set of dedupe_hashes already in the database for the user.
        
    Returns:
        A list of new, unique job dictionaries ready for processing.
    """
    new_jobs = []
    for job in jobs:
        # Generate the hash for the current job
        dedupe_hash = generate_dedupe_hash(job['job_title'], job['company_name'])
        
        # If the hash is not in our existing set, it's a new job
        if dedupe_hash not in existing_hashes:
            job['dedupe_hash'] = dedupe_hash
            new_jobs.append(job)
            # Add to the set to prevent duplicates from within the same scrape batch
            existing_hashes.add(dedupe_hash)
            
    return new_jobs
