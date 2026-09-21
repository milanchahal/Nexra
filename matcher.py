# backend/app/discovery/matcher.py
"""
Profile-to-Job matching algorithms.
Extracts keywords from profiles and calculates match scores.
"""
from app.models.profile import Profile
import re
from typing import Set, List

# Common words to ignore in matching
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
    'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have',
    'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
    'might', 'must', 'shall', 'can', 'need', 'about', 'above', 'after', 'before',
    'into', 'through', 'during', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'than', 'too', 'very', 'just', 'also', 'now', 'we', 'us', 'our', 'you', 'your',
    'work', 'working', 'experience', 'years', 'year', 'team', 'company', 'role',
}

# High-value tech keywords that boost matching
TECH_KEYWORDS = {
    'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
    'node', 'nodejs', 'django', 'flask', 'fastapi', 'spring', 'springboot',
    'aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'k8s', 'devops',
    'ci/cd', 'jenkins', 'git', 'github', 'gitlab', 'sql', 'mysql', 'postgresql',
    'mongodb', 'redis', 'elasticsearch', 'kafka', 'rabbitmq', 'graphql', 'rest',
    'api', 'microservices', 'machine', 'learning', 'ml', 'ai', 'artificial',
    'intelligence', 'deep', 'neural', 'tensorflow', 'pytorch', 'nlp', 'data',
    'analytics', 'science', 'scientist', 'engineer', 'developer', 'frontend',
    'backend', 'fullstack', 'full-stack', 'mobile', 'android', 'ios', 'flutter',
    'react-native', 'kotlin', 'swift', 'go', 'golang', 'rust', 'c++', 'scala',
    'hadoop', 'spark', 'airflow', 'tableau', 'powerbi', 'sre', 'reliability',
    'intern', 'internship', 'fresher', 'graduate', 'trainee', 'associate',
}

def get_keywords_from_profile(profile: Profile) -> List[str]:
    """
    Extracts a list of normalized keywords from a user's profile.
    Includes skills, experience roles, and resume text analysis.
    
    Returns:
        List of keywords (ordered by importance)
    """
    keywords = []
    seen = set()
    
    def add_keyword(word: str):
        word = word.lower().strip()
        if word and len(word) > 2 and word not in STOP_WORDS and word not in seen:
            seen.add(word)
            keywords.append(word)
    
    # 1. Add all skills (highest priority)
    for skill in profile.skills:
        # Handle multi-word skills
        add_keyword(skill)
        for word in skill.split():
            add_keyword(word)
    
    # 2. Add keywords from raw resume text
    if profile.raw_resume_text:
        # Extract words that match tech keywords
        words = re.findall(r'\b[a-zA-Z+#]+\b', profile.raw_resume_text.lower())
        for word in words:
            if word in TECH_KEYWORDS:
                add_keyword(word)
    
    # 3. Add keywords from experience roles
    for exp in profile.experiences:
        for word in re.split(r'[\s/,\-]+', exp.role):
            add_keyword(word)
        for bp in exp.bullet_points:
            for word in re.findall(r'\b[a-zA-Z+#]+\b', bp.lower()):
                if word in TECH_KEYWORDS:
                    add_keyword(word)
    
    return keywords

def calculate_match_score(job_title: str, job_description: str = "", user_keywords: List[str] = None) -> int:
    """
    Calculates a relevance score for a job based on keyword matching.
    
    Args:
        job_title: The title of the discovered job
        job_description: The job description text
        user_keywords: List of keywords from the user's profile
        
    Returns:
        An integer score between 0 and 100
    """
    if user_keywords is None:
        user_keywords = []
    
    user_keyword_set = set(kw.lower() for kw in user_keywords)
    
    # Combine title and description for matching
    combined_text = f"{job_title} {job_description}".lower()
    job_words = set(re.findall(r'\b[a-zA-Z+#]+\b', combined_text))
    
    score = 0
    
    # Count matching keywords
    matching_keywords = user_keyword_set.intersection(job_words)
    tech_matches = matching_keywords.intersection(TECH_KEYWORDS)
    
    # Scoring algorithm:
    # - Each matching keyword: 10 points
    # - Each tech keyword match: extra 5 points
    # - Title contains user keyword: extra 15 points
    
    score += len(matching_keywords) * 10
    score += len(tech_matches) * 5
    
    # Bonus for title matches (more relevant)
    title_words = set(job_title.lower().split())
    title_matches = user_keyword_set.intersection(title_words)
    score += len(title_matches) * 15
    
    # Boost for intern/fresher roles if user is entry-level
    intern_keywords = {'intern', 'internship', 'trainee', 'fresher', 'graduate', 'entry'}
    if job_words.intersection(intern_keywords) and user_keyword_set.intersection(intern_keywords):
        score += 20
    
    # Boost for specific role matches
    role_keywords = {'developer', 'engineer', 'architect', 'manager', 'analyst', 'scientist'}
    if job_words.intersection(role_keywords) and user_keyword_set.intersection(role_keywords):
        score += 10
    
    # Cap at 100
    return min(100, max(0, score))
