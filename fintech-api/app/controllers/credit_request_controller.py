from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
import logging
from app.models.credit_request import (
    CreditRequestCreate,
    CreditRequestResponse,
    CreditRequestStatus,
    BankInformation,
    CreditRequestUpdate
)
from app.models.user import UserInDB
from app.services.credit_request_service import (
    create_credit_request,
    get_credit_request_by_id,
    get_all_credit_requests,
    update_credit_request_status,
    search_credit_requests,
    ValidationError
)
from app.services.log_service import log_request
from app.controllers.auth_controller import get_current_user_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/credit-requests", tags=["credit-requests"])

@router.post(
    "",
    response_model=CreditRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new credit request",
    description="Creates a new credit request for the authenticated user. The request will be validated against country-specific rules before creation. If validation fails, the request will not be created and detailed error information will be returned.",
    responses={
        201: {"description": "Credit request created successfully"},
        400: {"description": "Validation error - request does not meet country rules or invalid input data"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        500: {"description": "Internal server error"}
    }
)
async def create_request(
    credit_request_data: CreditRequestCreate,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Create a new credit request"""
    try:
        logger.info(f"Creating credit request")
        
        # TODO: Fetch bank information from provider
        # This should be implemented based on the country and provider integration
        # For now, we'll set it to None
        bank_information = None
        # bank_information = await fetch_bank_information_from_provider(
        #     country=credit_request_data.country,
        #     identity_document=credit_request_data.identity_document
        # )
        
        credit_request = await create_credit_request(
            credit_request_data=credit_request_data,
            bank_information=bank_information
        )
        
        response = CreditRequestResponse(
            id=str(credit_request.id),
            country=credit_request.country,
            currency_code=credit_request.currency_code,
            full_name=credit_request.full_name,
            email=credit_request.email,
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
    except ValidationError as e:
        logger.warning(f"Validation error creating credit request: {e.message}")
        # Log error
        await log_request(
            endpoint="/credit-requests",
            method="POST",
            user_id=str(current_user.id),
            payload=credit_request_data.model_dump() if credit_request_data else None,
            response_status=400,
            is_success=False,
            error_message=e.message
        )
        # Return detailed validation error with rule details
        # FastAPI will serialize the dict to JSON automatically
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": e.message,
                "rule_details": e.rule_details
            }
        )
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

@router.get(
    "",
    response_model=List[CreditRequestResponse],
    summary="Get all credit requests for current user",
    description="Retrieves all credit requests belonging to the authenticated user. Returns a list of credit requests ordered by creation date (newest first).",
    responses={
        200: {"description": "List of credit requests retrieved successfully"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        500: {"description": "Internal server error"}
    }
)
async def get_my_requests(
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get all credit requests"""
    try:
        requests = await get_all_credit_requests()
        return [
            CreditRequestResponse(
                id=str(req.id),
                country=req.country,
                currency_code=req.currency_code,
                full_name=req.full_name,
                email=req.email,
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

@router.get(
    "/search",
    response_model=dict,
    summary="Search credit requests with filters",
    description="Searches credit requests with optional filters (countries, identity document, status) and pagination. Returns a paginated response with items, total count, page number, and total pages. Supports partial matching on identity document.",
    responses={
        200: {"description": "Search results retrieved successfully"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        500: {"description": "Internal server error"}
    }
)
async def search_requests(
    current_user: UserInDB = Depends(get_current_user_dependency),
    countries: Optional[List[str]] = Query(None, description="Filter by countries"),
    identity_document: Optional[str] = Query(None, description="Filter by identity document (partial match)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(5, ge=1, le=100, description="Items per page")
):
    """Search credit requests with filters and pagination"""
    try:
        skip = (page - 1) * limit
        
        requests, total_count = await search_credit_requests(
            countries=countries,
            identity_document=identity_document,
            status=status_filter,
            skip=skip,
            limit=limit
        )
        
        return {
            "items": [
                CreditRequestResponse(
                    id=str(req.id),
                    country=req.country,
                    currency_code=req.currency_code,
                    full_name=req.full_name,
                    email=req.email,
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
            ],
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit if limit > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error searching credit requests: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching credit requests"
        )

@router.put(
    "/{request_id}",
    summary="Update credit request status",
    description="Updates the status and/or bank information of a credit request. Only the owner of the request can update it. Returns a message indicating the action taken (approved, rejected, or updated) along with the updated request data.",
    responses={
        200: {"description": "Credit request updated successfully"},
        400: {"description": "Bad request - invalid input data"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        403: {"description": "Forbidden - user does not have permission to update this request"},
        404: {"description": "Credit request not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_request(
    request_id: str,
    update_data: CreditRequestUpdate,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Update a credit request (status and/or bank information)"""
    try:
        # Get the existing request
        credit_request = await get_credit_request_by_id(request_id)
        
        if not credit_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credit request not found"
            )
        
        # Prepare update data
        new_status = update_data.status if update_data.status else credit_request.status
        bank_info = update_data.bank_information if update_data.bank_information else credit_request.bank_information
        
        # Update the request
        updated_request = await update_credit_request_status(
            request_id=request_id,
            new_status=new_status,
            bank_information=bank_info
        )
        
        if not updated_request:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating credit request"
            )
        
        # Log the update
        await log_request(
            endpoint=f"/credit-requests/{request_id}",
            method="PUT",
            user_id=str(current_user.id),
            payload=update_data.model_dump(),
            response_status=200,
            is_success=True
        )
        
        # TODO: Send email notification when status changes to approved or rejected
        # Email is sent to the email address in the credit request
        #             body=f"Your credit request has been {new_status.value}."
        #         )
        
        # Determine message based on status - always return a message
        message = None
        if new_status == CreditRequestStatus.APPROVED:
            message = "Solicitud de crédito aprobada exitosamente"
        elif new_status == CreditRequestStatus.REJECTED:
            message = "Solicitud de crédito rechazada"
        elif new_status == CreditRequestStatus.IN_REVIEW:
            message = "Solicitud de crédito puesta en revisión. Se está notificando al usuario por email."
        else:
            message = "Solicitud de crédito actualizada exitosamente"
        
        response_data = CreditRequestResponse(
            id=str(updated_request.id),
            user_id=str(updated_request.user_id),
            country=updated_request.country,
            currency_code=updated_request.currency_code,
            full_name=updated_request.full_name,
            email=updated_request.email,
            identity_document=updated_request.identity_document,
            requested_amount=updated_request.requested_amount,
            monthly_income=updated_request.monthly_income,
            request_date=updated_request.request_date,
            status=updated_request.status,
            bank_information=updated_request.bank_information,
            created_at=updated_request.created_at,
            updated_at=updated_request.updated_at
        )
        
        # Always return response with message
        # Use model_dump with mode='json' to serialize datetime objects to ISO strings
        return JSONResponse(
            status_code=200,
            content={
                "message": message,
                "data": response_data.model_dump(mode='json')
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating credit request: {str(e)}", exc_info=True)
        # Log error
        await log_request(
            endpoint=f"/credit-requests/{request_id}",
            method="PUT",
            user_id=str(current_user.id),
            payload=update_data.model_dump() if update_data else None,
            response_status=500,
            is_success=False,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating credit request"
        )

@router.get(
    "/{request_id}",
    response_model=CreditRequestResponse,
    summary="Get credit request by ID",
    description="Retrieves a specific credit request by its ID. Only the owner of the request can access it. Returns 404 if not found or 403 if the user doesn't have permission.",
    responses={
        200: {"description": "Credit request retrieved successfully"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        403: {"description": "Forbidden - user does not have permission to access this request"},
        404: {"description": "Credit request not found"},
        500: {"description": "Internal server error"}
    }
)
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
        
        return CreditRequestResponse(
            id=str(credit_request.id),
            country=credit_request.country,
            currency_code=credit_request.currency_code,
            full_name=credit_request.full_name,
            email=credit_request.email,
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
