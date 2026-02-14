"""
Service for country rule business logic
"""
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
import logging
from app.models.country_rule import (
    CountryRuleCreate,
    CountryRuleUpdate,
    CountryRuleInDB,
    ValidationRule
)
from app.models.credit_request import Country
from app.repositories.country_rule_repository import country_rule_repository

logger = logging.getLogger(__name__)


async def create_country_rule(
    country_rule_data: CountryRuleCreate,
    created_by: Optional[str] = None
) -> CountryRuleInDB:
    """Create a new country rule"""
    logger.info(f"Creating country rule for {country_rule_data.country}")
    
    # Check if rule already exists for this country
    existing_rule = await country_rule_repository.get_by_country(country_rule_data.country)
    if existing_rule and existing_rule.is_active:
        raise ValueError(f"Active country rule already exists for {country_rule_data.country}")
    
    country_rule = CountryRuleInDB(
        country=country_rule_data.country,
        required_document_type=country_rule_data.required_document_type,
        description=country_rule_data.description,
        is_active=country_rule_data.is_active,
        validation_rules=country_rule_data.validation_rules,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by=ObjectId(created_by) if created_by else None,
        updated_by=None
    )
    
    return await country_rule_repository.create(country_rule)


async def get_country_rule_by_id(rule_id: str) -> Optional[CountryRuleInDB]:
    """Get country rule by ID"""
    return await country_rule_repository.get_by_id(rule_id)


async def get_country_rule_by_country(country: Country) -> Optional[CountryRuleInDB]:
    """Get active country rule for a specific country"""
    return await country_rule_repository.get_by_country(country)


async def get_all_country_rules(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[CountryRuleInDB]:
    """Get all country rules with pagination"""
    return await country_rule_repository.get_all(skip=skip, limit=limit, is_active=is_active)


async def update_country_rule(
    rule_id: str,
    update_data: CountryRuleUpdate,
    updated_by: Optional[str] = None
) -> Optional[CountryRuleInDB]:
    """Update a country rule"""
    logger.info(f"Updating country rule {rule_id}")
    
    # Convert update data to dict, excluding None values
    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
    
    if not update_dict:
        raise ValueError("No fields to update")
    
    return await country_rule_repository.update(rule_id, update_dict, updated_by)


async def delete_country_rule(rule_id: str) -> bool:
    """Soft delete a country rule (sets is_active=False)"""
    logger.info(f"Deleting country rule {rule_id}")
    return await country_rule_repository.delete(rule_id)


async def hard_delete_country_rule(rule_id: str) -> bool:
    """Permanently delete a country rule"""
    logger.info(f"Hard deleting country rule {rule_id}")
    return await country_rule_repository.hard_delete(rule_id)


async def count_country_rules(is_active: Optional[bool] = None) -> int:
    """Count country rules"""
    return await country_rule_repository.count(is_active)
