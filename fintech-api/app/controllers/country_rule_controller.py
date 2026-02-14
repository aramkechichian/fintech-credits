"""
API endpoints for country rules CRUD operations
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
import logging
from app.models.country_rule import (
    CountryRuleCreate,
    CountryRuleUpdate,
    CountryRuleResponse
)
from app.models.user import UserInDB
from app.models.credit_request import Country
from app.services.country_rule_service import (
    create_country_rule,
    get_country_rule_by_id,
    get_country_rule_by_country,
    get_all_country_rules,
    update_country_rule,
    delete_country_rule,
    count_country_rules
)
from app.services.log_service import log_request
from app.controllers.auth_controller import get_current_user_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/country-rules", tags=["country-rules"])


@router.post("", response_model=CountryRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    country_rule_data: CountryRuleCreate,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Create a new country rule"""
    try:
        logger.info(f"Creating country rule for {country_rule_data.country} by user {current_user.id}")
        
        country_rule = await create_country_rule(
            country_rule_data=country_rule_data,
            created_by=str(current_user.id)
        )
        
        response = CountryRuleResponse(
            id=str(country_rule.id),
            country=country_rule.country,
            required_document_type=country_rule.required_document_type,
            description=country_rule.description,
            is_active=country_rule.is_active,
            validation_rules=country_rule.validation_rules,
            created_at=country_rule.created_at,
            updated_at=country_rule.updated_at,
            created_by=str(country_rule.created_by) if country_rule.created_by else None,
            updated_by=str(country_rule.updated_by) if country_rule.updated_by else None
        )
        
        await log_request(
            endpoint="/country-rules",
            method="POST",
            user_id=str(current_user.id),
            payload=country_rule_data.model_dump(),
            response_status=201,
            is_success=True
        )
        
        return response
    except ValueError as e:
        logger.warning(f"Validation error creating country rule: {str(e)}")
        await log_request(
            endpoint="/country-rules",
            method="POST",
            user_id=str(current_user.id),
            payload=country_rule_data.model_dump() if country_rule_data else None,
            response_status=400,
            is_success=False,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating country rule: {str(e)}", exc_info=True)
        await log_request(
            endpoint="/country-rules",
            method="POST",
            user_id=str(current_user.id),
            payload=country_rule_data.model_dump() if country_rule_data else None,
            response_status=500,
            is_success=False,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating country rule"
        )


@router.get("", response_model=dict)
async def get_all_rules(
    current_user: UserInDB = Depends(get_current_user_dependency),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """Get all country rules with pagination"""
    try:
        rules = await get_all_country_rules(skip=skip, limit=limit, is_active=is_active)
        total = await count_country_rules(is_active=is_active)
        
        return {
            "items": [
                CountryRuleResponse(
                    id=str(rule.id),
                    country=rule.country,
                    required_document_type=rule.required_document_type,
                    description=rule.description,
                    is_active=rule.is_active,
                    validation_rules=rule.validation_rules,
                    created_at=rule.created_at,
                    updated_at=rule.updated_at,
                    created_by=str(rule.created_by) if rule.created_by else None,
                    updated_by=str(rule.updated_by) if rule.updated_by else None
                )
                for rule in rules
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting country rules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving country rules"
        )


@router.get("/{rule_id}", response_model=CountryRuleResponse)
async def get_rule(
    rule_id: str,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get a specific country rule by ID"""
    try:
        country_rule = await get_country_rule_by_id(rule_id)
        
        if not country_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country rule not found"
            )
        
        return CountryRuleResponse(
            id=str(country_rule.id),
            country=country_rule.country,
            required_document_type=country_rule.required_document_type,
            description=country_rule.description,
            is_active=country_rule.is_active,
            validation_rules=country_rule.validation_rules,
            created_at=country_rule.created_at,
            updated_at=country_rule.updated_at,
            created_by=str(country_rule.created_by) if country_rule.created_by else None,
            updated_by=str(country_rule.updated_by) if country_rule.updated_by else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting country rule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving country rule"
        )


@router.get("/country/{country}", response_model=CountryRuleResponse)
async def get_rule_by_country(
    country: Country,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get active country rule for a specific country"""
    try:
        country_rule = await get_country_rule_by_country(country)
        
        if not country_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active country rule not found for {country}"
            )
        
        return CountryRuleResponse(
            id=str(country_rule.id),
            country=country_rule.country,
            required_document_type=country_rule.required_document_type,
            description=country_rule.description,
            is_active=country_rule.is_active,
            validation_rules=country_rule.validation_rules,
            created_at=country_rule.created_at,
            updated_at=country_rule.updated_at,
            created_by=str(country_rule.created_by) if country_rule.created_by else None,
            updated_by=str(country_rule.updated_by) if country_rule.updated_by else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting country rule by country: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving country rule"
        )


@router.put("/{rule_id}", response_model=CountryRuleResponse)
async def update_rule(
    rule_id: str,
    update_data: CountryRuleUpdate,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Update a country rule"""
    try:
        country_rule = await get_country_rule_by_id(rule_id)
        
        if not country_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country rule not found"
            )
        
        updated_rule = await update_country_rule(
            rule_id=rule_id,
            update_data=update_data,
            updated_by=str(current_user.id)
        )
        
        if not updated_rule:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating country rule"
            )
        
        await log_request(
            endpoint=f"/country-rules/{rule_id}",
            method="PUT",
            user_id=str(current_user.id),
            payload=update_data.model_dump(),
            response_status=200,
            is_success=True
        )
        
        return CountryRuleResponse(
            id=str(updated_rule.id),
            country=updated_rule.country,
            required_document_type=updated_rule.required_document_type,
            description=updated_rule.description,
            is_active=updated_rule.is_active,
            validation_rules=updated_rule.validation_rules,
            created_at=updated_rule.created_at,
            updated_at=updated_rule.updated_at,
            created_by=str(updated_rule.created_by) if updated_rule.created_by else None,
            updated_by=str(updated_rule.updated_by) if updated_rule.updated_by else None
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error updating country rule: {str(e)}")
        await log_request(
            endpoint=f"/country-rules/{rule_id}",
            method="PUT",
            user_id=str(current_user.id),
            payload=update_data.model_dump() if update_data else None,
            response_status=400,
            is_success=False,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating country rule: {str(e)}", exc_info=True)
        await log_request(
            endpoint=f"/country-rules/{rule_id}",
            method="PUT",
            user_id=str(current_user.id),
            payload=update_data.model_dump() if update_data else None,
            response_status=500,
            is_success=False,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating country rule"
        )


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: str,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Delete a country rule (soft delete)"""
    try:
        country_rule = await get_country_rule_by_id(rule_id)
        
        if not country_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country rule not found"
            )
        
        deleted = await delete_country_rule(rule_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting country rule"
            )
        
        await log_request(
            endpoint=f"/country-rules/{rule_id}",
            method="DELETE",
            user_id=str(current_user.id),
            payload=None,
            response_status=204,
            is_success=True
        )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting country rule: {str(e)}", exc_info=True)
        await log_request(
            endpoint=f"/country-rules/{rule_id}",
            method="DELETE",
            user_id=str(current_user.id),
            payload=None,
            response_status=500,
            is_success=False,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting country rule"
        )
