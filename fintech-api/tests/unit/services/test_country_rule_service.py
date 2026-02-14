"""
Unit tests for CountryRuleService with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from bson import ObjectId
from app.models.country_rule import (
    CountryRuleCreate,
    CountryRuleUpdate,
    CountryRuleInDB,
    ValidationRule
)
from app.models.credit_request import Country
from app.services import country_rule_service


@pytest.fixture
def country_rule_data():
    """Create country rule data"""
    return CountryRuleCreate(
        country=Country.SPAIN,
        required_document_type="DNI",
        description="Test rule",
        is_active=True,
        validation_rules=[
            ValidationRule(
                max_percentage=30.0,
                enabled=True,
                error_message="Test error"
            )
        ]
    )


@pytest.fixture
def mock_country_rule():
    """Create a mock country rule"""
    return CountryRuleInDB(
        id=ObjectId("507f1f77bcf86cd799439012"),
        country=Country.SPAIN,
        required_document_type="DNI",
        description="Test rule",
        is_active=True,
        validation_rules=[
            ValidationRule(
                max_percentage=30.0,
                enabled=True,
                error_message="Test error"
            )
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by=ObjectId("507f1f77bcf86cd799439011"),
        updated_by=None
    )


@pytest.mark.asyncio
async def test_create_country_rule_success(country_rule_data, mock_country_rule):
    """Test successful country rule creation"""
    with patch('app.services.country_rule_service.country_rule_repository') as mock_repo:
        mock_repo.get_by_country = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(return_value=mock_country_rule)
        
        result = await country_rule_service.create_country_rule(
            country_rule_data=country_rule_data,
            created_by=str(ObjectId("507f1f77bcf86cd799439011"))
        )
        
        assert result.country == Country.SPAIN
        assert result.required_document_type == "DNI"
        mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_country_rule_duplicate(country_rule_data, mock_country_rule):
    """Test creating country rule when duplicate exists"""
    with patch('app.services.country_rule_service.country_rule_repository') as mock_repo:
        mock_repo.get_by_country = AsyncMock(return_value=mock_country_rule)
        
        with pytest.raises(ValueError) as exc_info:
            await country_rule_service.create_country_rule(
                country_rule_data=country_rule_data,
                created_by=None
            )
        
        assert "already exists" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_country_rule_by_id_found(mock_country_rule):
    """Test getting country rule by ID when found"""
    with patch('app.services.country_rule_service.country_rule_repository') as mock_repo:
        mock_repo.get_by_id = AsyncMock(return_value=mock_country_rule)
        
        result = await country_rule_service.get_country_rule_by_id(str(mock_country_rule.id))
        
        assert result == mock_country_rule
        mock_repo.get_by_id.assert_called_once_with(str(mock_country_rule.id))


@pytest.mark.asyncio
async def test_get_country_rule_by_id_not_found():
    """Test getting country rule by ID when not found"""
    with patch('app.services.country_rule_service.country_rule_repository') as mock_repo:
        mock_repo.get_by_id = AsyncMock(return_value=None)
        
        result = await country_rule_service.get_country_rule_by_id("507f1f77bcf86cd799439012")
        
        assert result is None


@pytest.mark.asyncio
async def test_get_country_rule_by_country_found(mock_country_rule):
    """Test getting country rule by country when found"""
    with patch('app.services.country_rule_service.country_rule_repository') as mock_repo:
        mock_repo.get_by_country = AsyncMock(return_value=mock_country_rule)
        
        result = await country_rule_service.get_country_rule_by_country(Country.SPAIN)
        
        assert result == mock_country_rule
        mock_repo.get_by_country.assert_called_once_with(Country.SPAIN)


@pytest.mark.asyncio
async def test_get_all_country_rules(mock_country_rule):
    """Test getting all country rules"""
    with patch('app.services.country_rule_service.country_rule_repository') as mock_repo:
        mock_repo.get_all = AsyncMock(return_value=[mock_country_rule])
        
        result = await country_rule_service.get_all_country_rules(skip=0, limit=100)
        
        assert len(result) == 1
        assert result[0] == mock_country_rule
        mock_repo.get_all.assert_called_once_with(skip=0, limit=100, is_active=None)


@pytest.mark.asyncio
async def test_update_country_rule_success(mock_country_rule):
    """Test successful country rule update"""
    update_data = CountryRuleUpdate(
        description="Updated description",
        is_active=False
    )
    
    rule_dict = mock_country_rule.model_dump()
    rule_dict.update({
        "description": "Updated description",
        "is_active": False,
        "updated_at": datetime.utcnow()
    })
    updated_rule = CountryRuleInDB(**rule_dict)
    
    with patch('app.services.country_rule_service.country_rule_repository') as mock_repo:
        mock_repo.update = AsyncMock(return_value=updated_rule)
        
        result = await country_rule_service.update_country_rule(
            rule_id=str(mock_country_rule.id),
            update_data=update_data,
            updated_by=str(ObjectId("507f1f77bcf86cd799439011"))
        )
        
        assert result.description == "Updated description"
        assert result.is_active is False
        mock_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_country_rule_no_fields():
    """Test updating country rule with no fields"""
    update_data = CountryRuleUpdate()
    
    with pytest.raises(ValueError) as exc_info:
        await country_rule_service.update_country_rule(
            rule_id="507f1f77bcf86cd799439012",
            update_data=update_data,
            updated_by=None
        )
    
    assert "No fields to update" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_country_rule_success():
    """Test successful country rule deletion"""
    with patch('app.services.country_rule_service.country_rule_repository') as mock_repo:
        mock_repo.delete = AsyncMock(return_value=True)
        
        result = await country_rule_service.delete_country_rule("507f1f77bcf86cd799439012")
        
        assert result is True
        mock_repo.delete.assert_called_once_with("507f1f77bcf86cd799439012")


@pytest.mark.asyncio
async def test_count_country_rules():
    """Test counting country rules"""
    with patch('app.services.country_rule_service.country_rule_repository') as mock_repo:
        mock_repo.count = AsyncMock(return_value=5)
        
        result = await country_rule_service.count_country_rules(is_active=True)
        
        assert result == 5
        # The service passes is_active as a positional argument
        mock_repo.count.assert_called_once()
        # Verify it was called with True
        assert mock_repo.count.call_args[0][0] == True
