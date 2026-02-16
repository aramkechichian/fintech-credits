"""
Unit tests for DataController with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from datetime import datetime
from bson import ObjectId
from io import BytesIO
from app.models.credit_request import (
    CreditRequestInDB,
    CreditRequestStatus,
    Country,
    CurrencyCode
)
from app.models.user import UserInDB
from app.controllers import data_controller


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
def mock_credit_request():
    """Create a mock credit request"""
    return CreditRequestInDB(
        id=ObjectId("507f1f77bcf86cd799439012"),
        country=Country.BRAZIL,
        currency_code=CurrencyCode.BRL,
        full_name="John Doe",
        email="john.doe@example.com",
        identity_document="123456789",
        requested_amount=10000.0,
        monthly_income=5000.0,
        request_date=datetime.utcnow(),
        status=CreditRequestStatus.PENDING,
        bank_information=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.mark.asyncio
async def test_get_available_fields(mock_user):
    """Test getting available fields for export"""
    result = await data_controller.get_export_fields(current_user=mock_user)
    
    assert "fields" in result
    assert "field_names" in result
    assert isinstance(result["fields"], dict)
    assert isinstance(result["field_names"], list)
    assert "id" in result["fields"]
    assert "country" in result["fields"]


@pytest.mark.asyncio
async def test_export_to_excel_with_date_filters(mock_user, mock_credit_request):
    """Test exporting credit requests with date filters"""
    with patch('app.controllers.data_controller.export_credit_requests_to_excel', new_callable=AsyncMock) as mock_export:
        excel_content = BytesIO(b"fake excel content")
        mock_export.return_value = excel_content
        
        result = await data_controller.export_to_excel(
            current_user=mock_user,
            request_date_from="2024-01-01",
            request_date_to="2024-01-31",
            fields=["id", "request_date"]
        )
        
        assert result is not None
        mock_export.assert_called_once()

