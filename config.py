# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings.
    """
    PROJECT_NAME: str = "Nexara AI Backend"
    PROJECT_VERSION: str = "0.1.0"
    
    # Auth
    SECRET_KEY: str # Used for signing JWTs

    # MongoDB
    MONGO_CONNECTION_STRING: str
    MONGO_DATABASE_NAME: str
    
    # Redis for Rate Limiting
    REDIS_URL: str

    # Anthropic Claude API Key
    ANTHROPIC_API_KEY: str

    # Render Deployment (for Keep-Alive)
    RENDER_EXTERNAL_URL: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
