from typing import Optional
from datetime import datetime
from app.core.database import get_database
from app.models.log_data import LogDataInDB
from bson import ObjectId

class LogDataRepository:
    def __init__(self):
        self.collection_name = "log_data"

    async def create(self, log_data: LogDataInDB) -> LogDataInDB:
        """Create a new log entry"""
        db = get_database()
        log_dict = log_data.model_dump(by_alias=True, exclude={"id"})
        result = await db[self.collection_name].insert_one(log_dict)
        log_data.id = result.inserted_id
        return log_data

    async def get_by_id(self, log_id: str) -> Optional[LogDataInDB]:
        """Get log entry by ID"""
        db = get_database()
        log_doc = await db[self.collection_name].find_one({"_id": ObjectId(log_id)})
        if log_doc:
            return LogDataInDB(**log_doc)
        return None

    async def get_by_user_id(self, user_id: str, limit: int = 100) -> list[LogDataInDB]:
        """Get logs for a specific user"""
        db = get_database()
        cursor = db[self.collection_name].find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(limit)
        logs = []
        async for doc in cursor:
            logs.append(LogDataInDB(**doc))
        return logs

    async def get_by_endpoint(self, endpoint: str, limit: int = 100) -> list[LogDataInDB]:
        """Get logs for a specific endpoint"""
        db = get_database()
        cursor = db[self.collection_name].find({"endpoint": endpoint}).sort("created_at", -1).limit(limit)
        logs = []
        async for doc in cursor:
            logs.append(LogDataInDB(**doc))
        return logs

log_data_repository = LogDataRepository()
