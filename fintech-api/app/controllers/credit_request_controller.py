from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import logging
from app.models.credit_request import (
    CreditRequestCreate,
    CreditRequestResponse,
    CreditRequestStatus,
    BankInformation
)
from app.models.user import UserInDB
from app.services.credit_request_service import (
    create_credit_request,
    get_credit_request_by_id,
    get_user_credit_requests,
    update_credit_request_status
)
from app.services.log_service import log_request
from app.controllers.auth_controller import get_current_user_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/credit-requests", tags=["credit-requests"])

@router.post("", response_model=CreditRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    credit_request_data: CreditRequestCreate,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Create a new credit request"""
    try:
        logger.info(f"Creating credit request for user {current_user.id}")
        
        # TODO: Fetch bank information from provider
        # This should be implemented based on the country and provider integration
        # For now, we'll set it to None
        bank_information = None
        # bank_information = await fetch_bank_information_from_provider(
        #     country=credit_request_data.country,
        #     identity_document=credit_request_data.identity_document
        # )
        
        credit_request = await create_credit_request(
            user_id=str(current_user.id),
            credit_request_data=credit_request_data,
            bank_information=bank_information
        )
        
        response = CreditRequestResponse(
            id=str(credit_request.id),
            user_id=str(credit_request.user_id),
            country=credit_request.country,
            currency_code=credit_request.currency_code,
            full_name=credit_request.full_name,
            identity_document=credit_request.identity_document,
            requested_amount=credit_request.requested_amount,
            monthly_income=credit_request.monthly_income,
            request_date=credit_request.request_date,
            status=credit_request.status,
            bank_information=credit_request.bank_information,
            created_at=credit_request.created_at,
            updated_at=credit_request.updated_at
        )
        
        # Log successful request (already logged in service, but log response too)
        await log_request(
            endpoint="/credit-requests",
            method="POST",
            user_id=str(current_user.id),
            payload=credit_request_data.model_dump(),
            response_status=201,
            is_success=True
        )
        
        return response
    except ValueError as e:
        logger.warning(f"Validation error creating credit request: {str(e)}")
        # Log error
        await log_request(
            endpoint="/credit-requests",
            method="POST",
            user_id=str(current_user.id),
            payload=credit_request_data.model_dump() if credit_request_data else None,
            response_status=400,
            is_success=False,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating credit request: {str(e)}", exc_info=True)
        # Log error
        await log_request(
            endpoint="/credit-requests",
            method="POST",
            user_id=str(current_user.id),
            payload=credit_request_data.model_dump() if credit_request_data else None,
            response_status=500,
            is_success=False,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating credit request"
        )

@router.get("", response_model=List[CreditRequestResponse])
async def get_my_requests(
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get all credit requests for the current user"""
    try:
        requests = await get_user_credit_requests(str(current_user.id))
        return [
            CreditRequestResponse(
                id=str(req.id),
                user_id=str(req.user_id),
                country=req.country,
                currency_code=req.currency_code,
                full_name=req.full_name,
                identity_document=req.identity_document,
                requested_amount=req.requested_amount,
                monthly_income=req.monthly_income,
                request_date=req.request_date,
                status=req.status,
                bank_information=req.bank_information,
                created_at=req.created_at,
                updated_at=req.updated_at
            )
            for req in requests
        ]
    except Exception as e:
        logger.error(f"Error getting user credit requests: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving credit requests"
        )

@router.get("/{request_id}", response_model=CreditRequestResponse)
async def get_request(
    request_id: str,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get a specific credit request by ID"""
    try:
        credit_request = await get_credit_request_by_id(request_id)
        
        if not credit_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit request not found"
            )
        
        # Verify the request belongs to the current user
        if str(credit_request.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this credit request"
            )
        
        return CreditRequestResponse(
            id=str(credit_request.id),
            user_id=str(credit_request.user_id),
            country=credit_request.country,
            currency_code=credit_request.currency_code,
            full_name=credit_request.full_name,
            identity_document=credit_request.identity_document,
            requested_amount=credit_request.requested_amount,
            monthly_income=credit_request.monthly_income,
            request_date=credit_request.request_date,
            status=credit_request.status,
            bank_information=credit_request.bank_information,
            created_at=credit_request.created_at,
            updated_at=credit_request.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting credit request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving credit request"
        )
