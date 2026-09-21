# backend/app/discovery/extractor.py
import json
import re
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic
from app.core.config import settings

client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

async def extract_job_details(job_description: str, job_title: str) -> Dict[str, Any]:
    """
    Extracts structured data from job description using Claude Haiku.
    Returns:
        {
            "salary_min": int | None,
            "salary_max": int | None,
            "salary_type": str | None (monthly/yearly/hourly),
            "work_mode": str | None (remote/onsite/hybrid),
            "duration": str | None,
            "location": str | None,
            "experience_required": str | None
        }
    """
    if not job_description:
        return {}

    prompt = f"""EXTRACT structured data from this job listing.
    
JOB TITLE: {job_title}
DESCRIPTION:
{job_description[:4000]}

RETURN JSON ONLY with these fields:
- salary_min: number (in INR/local currency, convert usually. If range is 10k-20k, min=10000. If 12 LPA, min=1200000)
- salary_max: number
- salary_type: "monthly" | "yearly" | "hourly"
- work_mode: "remote" | "onsite" | "hybrid"
- duration: string (e.g. "3 months", "6 months" - mostly for internships)
- location: string (City, Country - e.g. "Bangalore, India", "Remote")
- experience_required: string (e.g. "Fresher", "1-2 years")

Rules:
- If salary is not mentioned, return null.
- If stipent mentioned (e.g. 10k/month), set salary_min=10000, salary_type="monthly".
- Detect work mode accurately.
- Normalize location (remove 'Hiring in' etc).

JSON:"""

    try:
        response = await client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        json_str = content.strip()
        # Find JSON block if wrapped
        match = re.search(r'\{.*\}', json_str, re.DOTALL)
        if match:
            json_str = match.group(0)
            
        data = json.loads(json_str)
        return data
        
    except Exception as e:
        print(f"Extraction error: {e}")
        return {}
