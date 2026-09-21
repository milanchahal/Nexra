# app/core/db.py
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None

db = Database()

def get_db_client() -> AsyncIOMotorClient:
    """Returns the raw Motor client instance."""
    return db.client

def get_database_client() -> AsyncIOMotorClient:
    """Returns the raw Motor client instance (alias)."""
    return db.client

def get_database() -> AsyncIOMotorDatabase:
    """Returns the default database instance."""
    return db.client[settings.MONGO_DATABASE_NAME]

async def connect_to_mongo():
    """
    Connect to MongoDB.
    """
    print("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)
    print("MongoDB connection successful.")

async def close_mongo_connection():
    """
    Close MongoDB connection.
    """
    print("Closing MongoDB connection...")
    db.client.close()
    print("MongoDB connection closed.")