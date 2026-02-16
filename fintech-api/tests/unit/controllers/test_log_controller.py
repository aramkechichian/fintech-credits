"""
Unit tests for LogController with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from datetime import datetime
from bson import ObjectId
from io import BytesIO
from app.models.log_data import LogDataInDB
from app.models.user import UserInDB
from app.controllers import log_controller
from app.utils.endpoint_mapper import get_endpoints_for_module, get_module_name_for_endpoint


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
def mock_log_entry():
    """Create a mock log entry"""
    return LogDataInDB(
        id=ObjectId("507f1f77bcf86cd799439012"),
        endpoint="/credit-requests",
        method="POST",
        user_id=ObjectId("507f1f77bcf86cd799439011"),
        payload={"test": "data"},
        response_status=201,
        is_success=True,
        error_message=None,
        created_at=datetime.utcnow()
    )


@pytest.mark.asyncio
async def test_get_available_modules(mock_user):
    """Test getting available modules"""
    result = await log_controller.get_available_modules(current_user=mock_user)
    
    assert "modules" in result
    assert isinstance(result["modules"], list)
    assert "creditRequests" in result["modules"]


@pytest.mark.asyncio
async def test_search_logs_with_filters(mock_user, mock_log_entry):
    """Test searching logs with filters"""
    with patch('app.controllers.log_controller.search_logs', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([mock_log_entry], 1)
        
        result = await log_controller.search_logs_endpoint(
            current_user=mock_user,
            method="POST",
            module="creditRequests",
            date_from="2024-01-01",
            date_to="2024-01-31",
            page=1,
            limit=10
        )
        
        assert len(result["items"]) == 1
        mock_search.assert_called_once()


@pytest.mark.asyncio
async def test_search_logs_invalid_module(mock_user):
    """Test searching logs with invalid module"""
    result = await log_controller.search_logs_endpoint(
        current_user=mock_user,
        module="invalidModule",
        page=1,
        limit=10
    )
    
    # Should return empty results for invalid module
    assert result["items"] == []
    assert result["total"] == 0


@pytest.mark.asyncio
async def test_get_export_fields(mock_user):
    """Test getting export fields"""
    result = await log_controller.get_export_fields(current_user=mock_user)
    
    assert "fields" in result
    assert "field_names" in result
    assert isinstance(result["fields"], dict)
    assert isinstance(result["field_names"], list)

