from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId

class LogDataInDB(BaseModel):
    """Log data as stored in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    endpoint: str
    method: str  # GET, POST, PUT, DELETE, etc.
    user_id: Optional[ObjectId] = None  # User who made the request
    payload: Optional[dict] = None  # Request payload
    response_status: Optional[int] = None  # HTTP status code
    is_success: bool  # True if request was successful
    error_message: Optional[str] = None  # Error message if failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
