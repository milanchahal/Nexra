# app/services/ats_service.py
"""
ATS Resume Analysis and Optimization Service
Uses Claude API for keyword extraction and replacement suggestions
Jobright.ai style - ONLY suggests keyword swaps, NO full rewrite
"""
import os
import json
import re
from typing import Dict, Any, List, Optional
from anthropic import Anthropic


class ATSService:
    """ATS Resume Analysis using Claude API - Keyword-focused approach"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        if not api_key:
            print("Warning: No Anthropic API key found. ATS features will use fallback.")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
    
    async def extract_job_keywords(self, job_description: str, job_title: str) -> Dict[str, Any]:
        """
        Extract top 5-10 ATS keywords from job description.
        Returns JSON with keywords and skills.
        """
        if not self.client:
            return self._fallback_keywords(job_description)
        
        prompt = f"""You are a strict JSON-output assistant. Analyze this job posting and extract the most important ATS keywords.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_description[:2500]}

Return EXACT JSON only - no other text:
{{
    "keywords": ["keyword1", "keyword2", ...],
    "skills": ["skill1", "skill2", ...],
    "action_verbs": ["verb1", "verb2", ...]
}}

Rules:
- Return exactly valid JSON and nothing else
- Pick the 5-10 most relevant keywords for ATS matching
- Keywords should be short phrases (1-3 words max)
- Skills should be specific technical skills or tools
- Action verbs should be strong professional verbs from the job description"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = self._clean_json(response_text)
            return json.loads(response_text)
            
        except Exception as e:
            print(f"Keyword extraction error: {e}")
            return self._fallback_keywords(job_description)
    
    async def suggest_replacements(
        self, 
        resume_text: str, 
        job_description: str,
        job_title: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Suggest ONLY keyword replacements - no full rewrite.
        Returns max 10 surgical replacements.
        """
        if not self.client:
            return {"replacements": [], "keywords_used": keywords[:5]}
        
        # Extract relevant sections (skills + experience bullets)
        resume_excerpt = self._extract_relevant_sections(resume_text)
        
        prompt = f"""You are a STRICT resume skill optimizer. Your ONLY job is to find skills in the TECHNICAL SKILLS section that can be swapped.

## YOUR TASK:
Look at the "Technical Skills" or "Skills" section in the resume (usually near the bottom).
Find skills that are NOT required by this job and REPLACE them with skills that ARE required.

## JOB REQUIREMENTS:
Title: {job_title}
Required Skills: {json.dumps(keywords[:10])}
Job Description: {job_description[:2000]}

## RESUME TEXT (scroll to find "Technical Skills" section):
{resume_excerpt[:6000]}

## STRICT RULES - FOLLOW EXACTLY:
1. ONLY suggest replacements from the "Technical Skills" / "Skills" section
2. DO NOT touch the Summary, Header, Education, Experience, or any other section
3. Find skills in resume that job does NOT need (e.g., "MS Office", "Basic HTML")
4. Replace them with skills that job DOES need (from the required skills list above)
5. Keep replacement similar length (±40% characters) for PDF formatting
6. Maximum 5 replacements

## EXAMPLES OF GOOD REPLACEMENTS:
- If job needs "React" and resume has "jQuery" in skills → replace "jQuery" with "React"
- If job needs "AWS" and resume has "Azure" in skills → replace "Azure" with "AWS"
- If job needs "Python" and resume has "Java" but job doesn't need Java → replace "Java" with "Python"

## EXAMPLES OF BAD REPLACEMENTS (DO NOT DO THIS):
- Replacing "Mechanical Engineering" in Education section ❌
- Replacing text in the Summary/Profile section ❌
- Replacing company names or job titles ❌
- Replacing any text outside of Technical Skills section ❌

Return EXACT JSON only:
{{
    "replacements": [
        {{
            "original": "skill to replace (must be from Technical Skills section)",
            "replacement": "required skill from job",
            "context": "Technical Skills: Languages: C++, Python, [original]...",
            "reason": "Job requires [replacement] but not [original]",
            "max_occurrences": 1
        }}
    ]
}}

If you cannot find any valid skill swaps in the Technical Skills section, return: {{"replacements": []}}"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = self._clean_json(response_text)
            result = json.loads(response_text)
            
            # Validate and filter replacements
            validated = self._validate_replacements(result.get("replacements", []))
            
            return {
                "replacements": validated[:10],  # Max 10
                "keywords_used": keywords[:10],
                "total_suggested": len(result.get("replacements", []))
            }
            
        except Exception as e:
            print(f"Replacement suggestion error: {e}")
            return {"replacements": [], "keywords_used": keywords[:5], "error": str(e)}
    
    async def calculate_ats_score(
        self, 
        resume_text: str, 
        job_description: str,
        job_title: str
    ) -> Dict[str, Any]:
        """
        Calculate detailed ATS score for resume against job description
        """
        if not self.client:
            return self._fallback_score(resume_text, job_description)
        
        prompt = f"""Analyze this resume against the job description and provide an ATS compatibility score.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_description[:2500]}

RESUME:
{resume_text[:3500]}

Return EXACT JSON only:
{{
    "overall_score": <integer 0-100>,
    "skills_match": {{
        "score": <integer 0-100>,
        "matched_skills": ["skill1", "skill2"],
        "missing_skills": ["skill1", "skill2"]
    }},
    "experience_relevance": {{
        "score": <integer 0-100>,
        "relevant_experience": ["point1", "point2"],
        "gaps": ["gap1"]
    }},
    "keyword_optimization": {{
        "score": <integer 0-100>,
        "matched_keywords": ["kw1", "kw2"],
        "missing_keywords": ["kw1", "kw2"]
    }},
    "format_score": <integer 0-100>,
    "education_match": <integer 0-100>,
    "recommendations": ["rec1", "rec2", "rec3"],
    "strengths": ["strength1", "strength2"]
}}"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            response_text = self._clean_json(response_text)
            return json.loads(response_text)
            
        except Exception as e:
            print(f"ATS score calculation error: {e}")
            return self._fallback_score(resume_text, job_description)
    
    def _extract_relevant_sections(self, resume_text: str) -> str:
        """
        Extract most relevant sections for keyword matching:
        - Skills section
        - Experience bullets
        - Summary
        """
        lines = resume_text.split('\n')
        relevant_lines = []
        in_relevant_section = False
        section_markers = ['skill', 'experience', 'summary', 'project', 'work', 'technical']
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if entering a relevant section
            if any(marker in line_lower for marker in section_markers):
                in_relevant_section = True
            elif line_lower and len(line_lower) < 30 and ':' not in line_lower:
                # Might be a new section header
                if any(word in line_lower for word in ['education', 'certification', 'award', 'reference']):
                    in_relevant_section = False
            
            if in_relevant_section or len(relevant_lines) < 100:
                relevant_lines.append(line)
        
        return '\n'.join(relevant_lines[:300])  # Limit to 300 lines to ensure entire resume is captured if possible
    
    def _validate_replacements(self, replacements: List[Dict]) -> List[Dict]:
        """
        Validate replacement suggestions:
        - Length check (±30%)
        - Not empty
        - Reasonable word count
        """
        validated = []
        
        for r in replacements:
            original = r.get("original", "").strip()
            replacement = r.get("replacement", "").strip()
            
            if not original or not replacement:
                continue
            
            # Length check
            orig_len = len(original)
            repl_len = len(replacement)
            
            if orig_len > 0:
                length_ratio = repl_len / orig_len
                if 0.5 <= length_ratio <= 2.0:  # Allow 50% to 200% length
                    # Word count check
                    orig_words = len(original.split())
                    repl_words = len(replacement.split())
                    
                    if max(orig_words, repl_words) <= 6:  # Max 6 words
                        validated.append({
                            "original": original,
                            "replacement": replacement,
                            "context": r.get("context", ""),
                            "reason": r.get("reason", "ATS optimization"),
                            "max_occurrences": min(r.get("max_occurrences", 1), 3)  # Max 3 occurrences
                        })
        
        return validated
    
    def _clean_json(self, text: str) -> str:
        """Clean JSON from markdown code blocks"""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```json?\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        return text.strip()
    
    def _fallback_keywords(self, job_description: str) -> Dict[str, Any]:
        """Fallback keyword extraction without API"""
        job_lower = job_description.lower()
        
        tech_keywords = [
            'python', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'agile', 'api', 'rest', 'mongodb', 'postgresql',
            'typescript', 'java', 'c++', 'machine learning', 'ai', 'cloud',
            'microservices', 'ci/cd', 'devops', 'scrum', 'jira', 'fastapi'
        ]
        
        found_keywords = [kw for kw in tech_keywords if kw in job_lower]
        
        return {
            "keywords": found_keywords[:10],
            "skills": found_keywords[:8],
            "action_verbs": ["developed", "implemented", "designed", "led", "managed"]
        }
    
    def _fallback_score(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Fallback scoring without API"""
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        tech_keywords = [
            'python', 'javascript', 'react', 'node', 'sql', 'aws', 'docker',
            'git', 'agile', 'api', 'mongodb', 'typescript', 'java', 'c++'
        ]
        
        matched = [kw for kw in tech_keywords if kw in resume_lower and kw in job_lower]
        missing = [kw for kw in tech_keywords if kw in job_lower and kw not in resume_lower]
        
        base_score = min(75, 45 + len(matched) * 5)
        
        return {
            "overall_score": base_score,
            "skills_match": {
                "score": min(80, 50 + len(matched) * 6),
                "matched_skills": matched[:10],
                "missing_skills": missing[:5]
            },
            "experience_relevance": {"score": 65, "relevant_experience": [], "gaps": []},
            "keyword_optimization": {
                "score": min(75, 45 + len(matched) * 5),
                "matched_keywords": matched[:8],
                "missing_keywords": missing[:5]
            },
            "format_score": 75,
            "education_match": 70,
            "recommendations": [
                "Add job-specific keywords",
                "Quantify achievements with numbers",
                "Use strong action verbs"
            ],
            "strengths": ["Good technical skills coverage"]
        }


# Singleton instance
_ats_service = None

def get_ats_service() -> ATSService:
    global _ats_service
    if _ats_service is None:
        _ats_service = ATSService()
    return _ats_service
