"""
Controller for bank provider endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from app.models.credit_request import Country
from app.models.user import UserInDB
from app.services.bank_provider_service import get_bank_information
from app.controllers.auth_controller import get_current_user_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bank-provider", tags=["bank-provider"])


@router.get(
    "/information",
    summary="Get bank information from provider",
    description="Retrieves bank information from the provider for a given country and person. This endpoint is prepared for future integration with bank provider APIs. Currently returns a placeholder message indicating no API is connected. The architecture is ready to integrate country-specific bank providers when needed.",
    responses={
        200: {"description": "Bank information retrieved successfully (or not connected message)"},
        400: {"description": "Bad request - invalid country, empty full name or identity document"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        500: {"description": "Internal server error"}
    }
)
async def get_bank_information_endpoint(
    country: str = Query(..., description="Country code (Brazil, Mexico, Spain, Portugal, Italy, Colombia)"),
    full_name: str = Query(..., description="Full name of the person"),
    identity_document: str = Query(..., description="Identity document number"),
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """
    Get bank information from provider for a given country and person
    
    This endpoint is prepared for future integration with bank provider APIs.
    Currently returns a placeholder message indicating no API is connected.
    
    Args:
        country: Country code (Brazil, Mexico, Spain, etc.)
        full_name: Full name of the person
        identity_document: Identity document number
        
    Returns:
        JSON response with bank information or status message
    """
    try:
        # Validate country
        try:
            country_enum = Country(country)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid country: {country}. Valid countries: {[c.value for c in Country]}"
            )
        
        # Validate inputs
        if not full_name or not full_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name is required"
            )
        
        if not identity_document or not identity_document.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identity document is required"
            )
        
        logger.info(f"Bank information request for country: {country}, document: {identity_document}")
        
        # Get bank information from service
        result = await get_bank_information(
            country=country_enum,
            full_name=full_name.strip(),
            identity_document=identity_document.strip()
        )
        
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bank information: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving bank information"
        )
