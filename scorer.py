# backend/app/discovery/scorer.py
import re
from typing import Set, List
from app.models.job import ATSScore

def get_word_set(text: str) -> Set[str]:
    """Utility to get a normalized set of words from a text block."""
    if not text:
        return set()
    return set(re.findall(r'\b\w+\b', text.lower()))

def calculate_ats_score(
    optimized_resume_text: str, 
    job_description: str,
    user_skills: Set[str]
) -> ATSScore:
    """
    Calculates a structured ATS score by comparing the resume against the job description
    and the user's base skills.
    """
    if not job_description:
        return ATSScore()

    job_keywords = get_word_set(job_description)
    resume_keywords = get_word_set(optimized_resume_text)
    
    if not job_keywords:
        return ATSScore()

    # 1. Overall Score (Keyword Overlap)
    matching_keywords = resume_keywords.intersection(job_keywords)
    overlap_percentage = (len(matching_keywords) / len(job_keywords)) * 100
    score = min(100, int(overlap_percentage))

    # 2. Skill Matching
    job_skills_present = user_skills.intersection(job_keywords)
    skills_matched = len(job_skills_present)
    total_skills_in_job = len(user_skills.union(job_keywords)) # A rough proxy

    # 3. Top Missing Skills
    potential_skills_in_job = job_keywords.intersection(user_skills) # Skills from JD that are also in user's general skillset
    missing_skills = potential_skills_in_job - resume_keywords
    top_missing_skills = list(missing_skills)[:5] # Show up to 5

    # 4. Title Alignment
    # This is a heuristic. A more advanced implementation could use word embeddings.
    title_alignment = "low"
    if score > 65:
        title_alignment = "high"
    elif score > 40:
        title_alignment = "medium"

    return ATSScore(
        score=score,
        skills_matched=skills_matched,
        total_skills_in_job=total_skills_in_job,
        top_missing_skills=top_missing_skills,
        title_alignment=title_alignment
    )