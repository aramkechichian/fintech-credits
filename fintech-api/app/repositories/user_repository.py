from typing import Optional
from app.core.database import get_database
from app.models.user import UserInDB
from bson import ObjectId

class UserRepository:
    def __init__(self):
        self.collection_name = "users"

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        db = get_database()
        user_doc = await db[self.collection_name].find_one({"email": email})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        db = get_database()
        user_doc = await db[self.collection_name].find_one({"_id": ObjectId(user_id)})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def create(self, user: UserInDB) -> UserInDB:
        """Create a new user"""
        db = get_database()
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        result = await db[self.collection_name].insert_one(user_dict)
        user.id = result.inserted_id
        return user

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        db = get_database()
        count = await db[self.collection_name].count_documents({"email": email}, limit=1)
        return count > 0

user_repository = UserRepository()
