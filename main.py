# app/main.py
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Try to import FastAPILimiter (may fail on some versions)
try:
    from fastapi_limiter import FastAPILimiter
    HAS_LIMITER = True
except ImportError:
    HAS_LIMITER = False
    print("⚠️ FastAPILimiter not available, rate limiting disabled")

# Load environment variables from .env file for local development
load_dotenv()

from app.core.config import settings
from app.core.db import connect_to_mongo, close_mongo_connection, get_database_client
from app.api.routers import api_router
from app.discovery.clawd_agent import initialize_agent, shutdown_agent

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# CORS middleware - fully open for all deployment platforms
# NOTE: allow_credentials must be False when allow_origins is ["*"]
# per the CORS spec. This is fine because we use Bearer token auth
# (Authorization header), not cookies, so credentials mode is not needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Connect to databases
    await connect_to_mongo()
    
    # Initialize the rate limiter (if available and Redis configured)
    if HAS_LIMITER and settings.REDIS_URL:
        try:
            redis_connection = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
            await FastAPILimiter.init(redis_connection)
            print("✅ Rate limiter initialized")
        except Exception as e:
            print(f"⚠️ Rate limiter init failed: {e}")
    
    # Initialize and start the job discovery agent
    db_client = get_database_client()
    initialize_agent(db_client)

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    shutdown_agent()

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Print the full traceback to the server logs
    traceback.print_exc()
    # Return a 500 response with explicit CORS headers so the browser doesn't block it
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Job Companion Backend"}

