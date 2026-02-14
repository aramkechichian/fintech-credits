"""
Unit tests for CountryRuleController with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status
from datetime import datetime
from bson import ObjectId
from app.models.country_rule import (
    CountryRuleCreate,
    CountryRuleUpdate,
    CountryRuleResponse,
    CountryRuleInDB,
    ValidationRule
)
from app.models.user import UserInDB
from app.models.credit_request import Country
from app.controllers import country_rule_controller


@pytest.fixture
def mock_user():
    """Create a mock user"""
    return UserInDB(
        id=ObjectId("507f1f77bcf86cd799439011"),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True
    )


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
async def test_create_rule_success(mock_user, country_rule_data, mock_country_rule):
    """Test successful rule creation"""
    with patch('app.controllers.country_rule_controller.create_country_rule', new_callable=AsyncMock) as mock_create, \
         patch('app.controllers.country_rule_controller.log_request', new_callable=AsyncMock) as mock_log:
        
        mock_create.return_value = mock_country_rule
        
        result = await country_rule_controller.create_rule(
            country_rule_data=country_rule_data,
            current_user=mock_user
        )
        
        assert isinstance(result, CountryRuleResponse)
        assert result.country == Country.SPAIN
        assert result.required_document_type == "DNI"
        mock_create.assert_called_once()
        mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_create_rule_validation_error(mock_user, country_rule_data):
    """Test rule creation with validation error"""
    with patch('app.controllers.country_rule_controller.create_country_rule', new_callable=AsyncMock) as mock_create, \
         patch('app.controllers.country_rule_controller.log_request', new_callable=AsyncMock) as mock_log:
        
        mock_create.side_effect = ValueError("Active country rule already exists")
        
        with pytest.raises(HTTPException) as exc_info:
            await country_rule_controller.create_rule(
                country_rule_data=country_rule_data,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_rules_success(mock_user, mock_country_rule):
    """Test getting all rules"""
    with patch('app.controllers.country_rule_controller.get_all_country_rules', new_callable=AsyncMock) as mock_get_all, \
         patch('app.controllers.country_rule_controller.count_country_rules', new_callable=AsyncMock) as mock_count:
        
        mock_get_all.return_value = [mock_country_rule]
        mock_count.return_value = 1
        
        result = await country_rule_controller.get_all_rules(
            current_user=mock_user,
            skip=0,
            limit=100
        )
        
        assert "items" in result
        assert "total" in result
        assert len(result["items"]) == 1
        assert result["total"] == 1


@pytest.mark.asyncio
async def test_get_rule_by_id_success(mock_user, mock_country_rule):
    """Test getting rule by ID"""
    with patch('app.controllers.country_rule_controller.get_country_rule_by_id', new_callable=AsyncMock) as mock_get:
        
        mock_get.return_value = mock_country_rule
        
        result = await country_rule_controller.get_rule(
            rule_id=str(mock_country_rule.id),
            current_user=mock_user
        )
        
        assert isinstance(result, CountryRuleResponse)
        assert result.country == Country.SPAIN


@pytest.mark.asyncio
async def test_get_rule_by_id_not_found(mock_user):
    """Test getting rule by ID when not found"""
    with patch('app.controllers.country_rule_controller.get_country_rule_by_id', new_callable=AsyncMock) as mock_get:
        
        mock_get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await country_rule_controller.get_rule(
                rule_id="507f1f77bcf86cd799439012",
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_rule_by_country_success(mock_user, mock_country_rule):
    """Test getting rule by country"""
    with patch('app.controllers.country_rule_controller.get_country_rule_by_country', new_callable=AsyncMock) as mock_get:
        
        mock_get.return_value = mock_country_rule
        
        result = await country_rule_controller.get_rule_by_country(
            country=Country.SPAIN,
            current_user=mock_user
        )
        
        assert isinstance(result, CountryRuleResponse)
        assert result.country == Country.SPAIN


@pytest.mark.asyncio
async def test_get_rule_by_country_not_found(mock_user):
    """Test getting rule by country when not found"""
    with patch('app.controllers.country_rule_controller.get_country_rule_by_country', new_callable=AsyncMock) as mock_get:
        
        mock_get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await country_rule_controller.get_rule_by_country(
                country=Country.SPAIN,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_rule_success(mock_user, mock_country_rule):
    """Test successful rule update"""
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
    
    with patch('app.controllers.country_rule_controller.get_country_rule_by_id', new_callable=AsyncMock) as mock_get, \
         patch('app.controllers.country_rule_controller.update_country_rule', new_callable=AsyncMock) as mock_update, \
         patch('app.controllers.country_rule_controller.log_request', new_callable=AsyncMock) as mock_log:
        
        mock_get.return_value = mock_country_rule
        mock_update.return_value = updated_rule
        
        result = await country_rule_controller.update_rule(
            rule_id=str(mock_country_rule.id),
            update_data=update_data,
            current_user=mock_user
        )
        
        assert isinstance(result, CountryRuleResponse)
        assert result.description == "Updated description"
        assert result.is_active is False
        mock_update.assert_called_once()
        mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_rule_not_found(mock_user):
    """Test updating rule when not found"""
    update_data = CountryRuleUpdate(description="Updated")
    
    with patch('app.controllers.country_rule_controller.get_country_rule_by_id', new_callable=AsyncMock) as mock_get:
        
        mock_get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await country_rule_controller.update_rule(
                rule_id="507f1f77bcf86cd799439012",
                update_data=update_data,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_rule_success(mock_user, mock_country_rule):
    """Test successful rule deletion"""
    with patch('app.controllers.country_rule_controller.get_country_rule_by_id', new_callable=AsyncMock) as mock_get, \
         patch('app.controllers.country_rule_controller.delete_country_rule', new_callable=AsyncMock) as mock_delete, \
         patch('app.controllers.country_rule_controller.log_request', new_callable=AsyncMock) as mock_log:
        
        mock_get.return_value = mock_country_rule
        mock_delete.return_value = True
        
        result = await country_rule_controller.delete_rule(
            rule_id=str(mock_country_rule.id),
            current_user=mock_user
        )
        
        assert result is None
        mock_delete.assert_called_once()
        mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_delete_rule_not_found(mock_user):
    """Test deleting rule when not found"""
    with patch('app.controllers.country_rule_controller.get_country_rule_by_id', new_callable=AsyncMock) as mock_get:
        
        mock_get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await country_rule_controller.delete_rule(
                rule_id="507f1f77bcf86cd799439012",
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
