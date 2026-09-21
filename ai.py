# backend/app/core/ai.py
import os
import re
import anthropic
from pydantic import ValidationError

from app.core.prompts import (
    get_ats_optimization_prompt,
    get_profile_extraction_prompt,
    get_match_explanation_prompt,
)
from app.models.profile import ProfileCreate

# Use the async client with FastAPI and Motor
client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

class AIService:
    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.model = model

    async def extract_profile_from_text(self, resume_text: str, max_retries: int = 3) -> ProfileCreate:
        system_prompt, user_prompt = get_profile_extraction_prompt(resume_text)
        for attempt in range(max_retries):
            try:
                response = await client.messages.create(
                    model=self.model, max_tokens=2048, system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}], temperature=0.0
                )
                return ProfileCreate.parse_raw(response.content[0].text)
            except (ValidationError, ValueError, IndexError) as e:
                print(f"Validation failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise ConnectionError("AI service failed to produce valid profile data.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                if attempt == max_retries - 1:
                    raise

    async def optimize_resume_for_job(self, original_resume_text: str, job_description: str, custom_instructions: str = None) -> str:
        system_prompt, user_prompt = get_ats_optimization_prompt(original_resume_text, job_description, custom_instructions)
        response = await client.messages.create(
            model=self.model, max_tokens=4096, system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}], temperature=0.2
        )
        text = response.content[0].text
        match = re.search(r'<optimized_resume>(.*?)</optimized_resume>', text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()

    async def generate_match_explanation(self, profile_summary: str, profile_skills: list, job_title: str, job_description: str) -> str:
        """
        Generates the 'Why you're a good match' explanation.
        """
        system_prompt, user_prompt = get_match_explanation_prompt(profile_summary, profile_skills, job_title, job_description)
        response = await client.messages.create(
            model=self.model, max_tokens=1024, system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}], temperature=0.3
        )
        return response.content[0].text.strip()

ai_service = AIService()
