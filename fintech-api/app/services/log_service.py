"""
Log service for logging and querying logs
"""
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
import logging
from app.models.log_data import LogDataInDB
from app.repositories.log_data_repository import log_data_repository

logger = logging.getLogger(__name__)

async def log_request(
    endpoint: str,
    method: str,
    user_id: Optional[str] = None,
    payload: Optional[dict] = None,
    response_status: Optional[int] = None,
    is_success: bool = True,
    error_message: Optional[str] = None
) -> LogDataInDB:
    """
    Log a request to the database
    
    Args:
        endpoint: The API endpoint (e.g., "/credit-requests")
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        user_id: ID of the user who made the request (optional)
        payload: Request payload/body (optional)
        response_status: HTTP response status code (optional)
        is_success: Whether the request was successful
        error_message: Error message if request failed (optional)
    
    Returns:
        LogDataInDB: The created log entry
    """
    try:
        # Sanitize payload (remove sensitive data like passwords)
        sanitized_payload = None
        if payload:
            sanitized_payload = payload.copy()
            # Remove sensitive fields
            sensitive_fields = ["password", "hashed_password", "access_token", "refresh_token"]
            for field in sensitive_fields:
                if field in sanitized_payload:
                    sanitized_payload[field] = "***"
        
        log_entry = LogDataInDB(
            endpoint=endpoint,
            method=method,
            user_id=ObjectId(user_id) if user_id else None,
            payload=sanitized_payload,
            response_status=response_status,
            is_success=is_success,
            error_message=error_message,
            created_at=datetime.utcnow()
        )
        
        created_log = await log_data_repository.create(log_entry)
        logger.debug(f"Log entry created: {created_log.id} for endpoint {endpoint}")
        return created_log
    except Exception as e:
        # Don't fail the request if logging fails
        logger.error(f"Error creating log entry: {str(e)}", exc_info=True)
        # Return a dummy log entry so the calling code doesn't break
        return LogDataInDB(
            endpoint=endpoint,
            method=method,
            user_id=ObjectId(user_id) if user_id else None,
            payload=payload,
            response_status=response_status,
            is_success=is_success,
            error_message=error_message,
            created_at=datetime.utcnow()
        )


async def search_logs(
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
    return await log_data_repository.search(
        method=method,
        endpoint=endpoint,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit
    )
