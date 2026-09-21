# backend/app/api/endpoints/discovery.py
from fastapi import APIRouter, Depends, BackgroundTasks, status
from app.core.auth import get_current_user
from app.core.db import get_db_client
from app.models.user import User

router = APIRouter()

async def run_discovery_for_user(user_id: str):
    """Background task to run discovery for a user."""
    from app.discovery.clawd_agent import ClawdJobDiscoveryAgent
    
    try:
        client = get_db_client()
        if client:
            agent = ClawdJobDiscoveryAgent(client)
            await agent.run_discovery_for_user(user_id)
    except Exception as e:
        print(f"Discovery error for user {user_id}: {e}")

@router.post(
    "/discovery/run",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Manual Job Discovery",
)
async def trigger_discovery_run(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Manually triggers a job discovery cycle for the currently authenticated user.
    """
    background_tasks.add_task(run_discovery_for_user, str(current_user.id))
    
    return {"message": "Job discovery process has been started for the user."}