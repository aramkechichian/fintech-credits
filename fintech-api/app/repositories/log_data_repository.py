from typing import Optional
from datetime import datetime, timedelta
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

    async def search(
        self,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[LogDataInDB], int]:
        """
        Search logs with filters and pagination
        
        Returns:
            tuple: (list of logs, total count)
        """
        db = get_database()
        
        # Build query
        query = {}
        
        # Filter by method
        if method:
            query["method"] = method.upper()
        
        # Filter by endpoint (partial match, case insensitive)
        # Can be a single endpoint or a list of endpoints (for module filtering)
        if endpoint:
            if isinstance(endpoint, list):
                # Multiple endpoints - use $in or $or for regex matching
                query["$or"] = [
                    {"endpoint": {"$regex": ep, "$options": "i"}}
                    for ep in endpoint
                ]
            else:
                query["endpoint"] = {"$regex": endpoint, "$options": "i"}
        
        # Filter by date range
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to + timedelta(days=1)
            query["created_at"] = date_query
        
        # Get total count
        total_count = await db[self.collection_name].count_documents(query)
        
        # Get paginated results
        cursor = db[self.collection_name].find(query).skip(skip).limit(limit).sort("created_at", -1)
        logs = []
        async for doc in cursor:
            logs.append(LogDataInDB(**doc))
        
        return logs, total_count

log_data_repository = LogDataRepository()
