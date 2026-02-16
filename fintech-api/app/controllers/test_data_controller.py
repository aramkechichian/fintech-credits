"""
Test data controller
Handles test data generation and cleanup endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict
import logging

from app.models.user import UserInDB
from app.controllers.auth_controller import get_current_user_dependency
from app.services.test_data_service import (
    generate_random_credit_requests,
    clear_all_credit_requests
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/test-data", tags=["test-data"])


@router.post(
    "/credit-requests/generate",
    response_model=Dict,
    status_code=status.HTTP_201_CREATED,
    summary="Generate random credit requests",
    description="Generate a specified number of random credit requests for testing purposes. Creates requests with varied countries, statuses, amounts, and dates.",
    responses={
        201: {"description": "Credit requests generated successfully"},
        400: {"description": "Invalid request"},
        500: {"description": "Error generating credit requests"}
    }
)
async def generate_credit_requests(
    count: int = 50,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """
    Generate random credit requests for testing
    
    Query parameters:
    - count: Number of requests to generate (default: 50, max: 100)
    """
    try:
        # Limit to reasonable number
        if count < 1 or count > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Count must be between 1 and 100"
            )
        
        logger.info(f"User {current_user.id} generating {count} test credit requests")
        
        created_requests = await generate_random_credit_requests(count=count)
        
        return {
            "message": f"Successfully generated {len(created_requests)} credit requests",
            "count": len(created_requests),
            "requested_count": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating credit requests: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating credit requests"
        )


@router.delete(
    "/credit-requests/clear",
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary="Clear all credit requests",
    description="Delete all credit requests from the database. Use with caution as this action cannot be undone.",
    responses={
        200: {"description": "All credit requests deleted successfully"},
        500: {"description": "Error clearing credit requests"}
    }
)
async def clear_credit_requests(
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """
    Delete all credit requests from the database
    """
    try:
        logger.info(f"User {current_user.id} clearing all credit requests")
        
        deleted_count = await clear_all_credit_requests()
        
        return {
            "message": f"Successfully deleted {deleted_count} credit requests",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing credit requests: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing credit requests"
        )
