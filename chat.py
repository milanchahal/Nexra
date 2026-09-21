"""
Chat API endpoint - Clawd AI Assistant
Uses Claude Haiku API for job-specific conversations
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import anthropic
import os

router = APIRouter(tags=["chat"])

# Initialize Claude client
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    job_context: Optional[dict] = None  # Current job details
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    suggested_prompts: List[str]

# Suggested prompts based on context
JOB_PROMPTS = [
    "Why is this job a good fit for me?",
    "Give me resume tips for this job",
    "Generate a custom resume tailored to this job",
    "Show me connections for potential referral",
    "Write a cover letter for this job",
    "What skills should I highlight?",
    "How can I improve my match score?",
]

GENERAL_PROMPTS = [
    "Adjust my job search preferences",
    "Find top matching jobs",
    "Help me prepare for interviews",
    "Review my resume",
]

def get_system_prompt(job_context: Optional[dict] = None) -> str:
    """Generate system prompt with job context"""
    base_prompt = """You are Clawd, an AI career assistant. You help users with:
- Job search and matching
- Resume optimization
- Interview preparation
- Career advice

Be helpful, concise, and actionable. Use emojis sparingly to be friendly.
When discussing specific jobs, provide concrete, tailored advice.
"""
    
    if job_context:
        job_info = f"""
CURRENT JOB CONTEXT:
- Title: {job_context.get('job_title', 'N/A')}
- Company: {job_context.get('company_name', 'N/A')}
- Location: {job_context.get('location', 'N/A')}
- Match Score: {job_context.get('match_score', 'N/A')}%
- Description: {job_context.get('job_description', 'N/A')[:1000]}
- Source: {job_context.get('source', 'N/A')}

The user is currently viewing this job. Provide advice specific to this role.
"""
        return base_prompt + job_info
    
    return base_prompt

@router.post("/", response_model=ChatResponse)
async def chat_with_clawd(request: ChatRequest):
    """Chat with Clawd AI assistant about jobs"""
    
    if not CLAUDE_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Claude API key not configured. Add ANTHROPIC_API_KEY to .env"
        )
    
    try:
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        
        # Build messages
        messages = []
        
        # Add conversation history
        for msg in request.conversation_history or []:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Call Claude Haiku
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=get_system_prompt(request.job_context),
            messages=messages
        )
        
        # Get response text
        response_text = response.content[0].text
        
        # Determine suggested prompts based on context
        prompts = JOB_PROMPTS[:5] if request.job_context else GENERAL_PROMPTS
        
        return ChatResponse(
            response=response_text,
            suggested_prompts=prompts
        )
        
    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/generate-resume")
async def generate_resume_for_job(job_id: str, user_resume: str):
    """Generate a tailored resume for a specific job"""
    
    if not CLAUDE_API_KEY:
        raise HTTPException(status_code=500, detail="Claude API key not configured")
    
    # This would fetch job from DB and generate tailored resume
    # For now, return placeholder
    return {"message": "Resume generation endpoint - to be implemented with job service"}


@router.post("/cover-letter")
async def generate_cover_letter(job_id: str):
    """Generate a cover letter for a specific job"""
    
    if not CLAUDE_API_KEY:
        raise HTTPException(status_code=500, detail="Claude API key not configured")
    
    return {"message": "Cover letter generation endpoint - to be implemented"}
