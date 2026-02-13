from typing import Optional, List
from datetime import datetime
from app.core.database import get_database
from app.models.credit_request import CreditRequestInDB
from bson import ObjectId

class CreditRequestRepository:
    def __init__(self):
        self.collection_name = "credit_requests"

    async def create(self, credit_request: CreditRequestInDB) -> CreditRequestInDB:
        """Create a new credit request"""
        db = get_database()
        credit_request_dict = credit_request.model_dump(by_alias=True, exclude={"id"})
        result = await db[self.collection_name].insert_one(credit_request_dict)
        credit_request.id = result.inserted_id
        return credit_request

    async def get_by_id(self, request_id: str) -> Optional[CreditRequestInDB]:
        """Get credit request by ID"""
        db = get_database()
        request_doc = await db[self.collection_name].find_one({"_id": ObjectId(request_id)})
        if request_doc:
            return CreditRequestInDB(**request_doc)
        return None

    async def get_by_user_id(self, user_id: str) -> List[CreditRequestInDB]:
        """Get all credit requests for a user"""
        db = get_database()
        cursor = db[self.collection_name].find({"user_id": ObjectId(user_id)})
        requests = []
        async for doc in cursor:
            requests.append(CreditRequestInDB(**doc))
        return requests

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CreditRequestInDB]:
        """Get all credit requests with pagination"""
        db = get_database()
        cursor = db[self.collection_name].find().skip(skip).limit(limit).sort("created_at", -1)
        requests = []
        async for doc in cursor:
            requests.append(CreditRequestInDB(**doc))
        return requests

    async def search(
        self,
        user_id: Optional[str] = None,
        countries: Optional[List[str]] = None,
        identity_document: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[CreditRequestInDB], int]:
        """
        Search credit requests with filters and pagination
        
        Returns:
            tuple: (list of requests, total count)
        """
        db = get_database()
        
        # Build query
        query = {}
        
        # Filter by user_id (users can only see their own requests)
        if user_id:
            query["user_id"] = ObjectId(user_id)
        
        # Filter by countries
        if countries and len(countries) > 0:
            query["country"] = {"$in": countries}
        
        # Filter by identity document (partial match, case insensitive)
        if identity_document:
            query["identity_document"] = {"$regex": identity_document, "$options": "i"}
        
        # Filter by status
        if status:
            query["status"] = status
        
        # Get total count
        total_count = await db[self.collection_name].count_documents(query)
        
        # Get paginated results
        cursor = db[self.collection_name].find(query).skip(skip).limit(limit).sort("created_at", -1)
        requests = []
        async for doc in cursor:
            requests.append(CreditRequestInDB(**doc))
        
        return requests, total_count

    async def update(self, request_id: str, update_data: dict) -> Optional[CreditRequestInDB]:
        """Update a credit request"""
        db = get_database()
        update_data["updated_at"] = datetime.utcnow()
        result = await db[self.collection_name].update_one(
            {"_id": ObjectId(request_id)},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await self.get_by_id(request_id)
        return None

    async def delete(self, request_id: str) -> bool:
        """Delete a credit request"""
        db = get_database()
        result = await db[self.collection_name].delete_one({"_id": ObjectId(request_id)})
        return result.deleted_count > 0

credit_request_repository = CreditRequestRepository()
