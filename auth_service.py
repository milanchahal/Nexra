# backend/app/services/auth_service.py
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import EmailStr

from app.core.auth import get_password_hash, verify_password
from app.models.user import User

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db.get_collection("users")

    async def register_user(self, email: EmailStr, password: str) -> User:
        """
        Registers a new user, checking for email uniqueness.
        """
        existing_user = await self.db.find_one({"email": email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )
        
        hashed_password = get_password_hash(password)
        new_user = User(email=email, hashed_password=hashed_password)
        
        await self.db.insert_one(new_user.dict(by_alias=True))
        
        # Return the created user model (without the password hash)
        created_user_data = await self.db.find_one({"email": email})
        return User(**created_user_data)

    async def authenticate_user(self, email: EmailStr, password: str) -> User | None:
        """
        Authenticates a user by email and password.
        Returns the user object if successful, otherwise None.
        """
        user_data = await self.db.find_one({"email": email})
        if not user_data:
            return None
        
        user = User(**user_data)
        if not verify_password(password, user.hashed_password):
            return None
            
        return user
