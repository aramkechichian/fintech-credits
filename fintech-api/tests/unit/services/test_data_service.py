"""
Unit tests for DataService with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from bson import ObjectId
from io import BytesIO
from app.models.credit_request import (
    CreditRequestInDB,
    CreditRequestStatus,
    Country,
    CurrencyCode
)
from app.services.data_service import (
    export_credit_requests_to_excel,
    get_available_fields,
    AVAILABLE_FIELDS
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
async def test_get_available_fields():
    """Test getting available fields for export"""
    fields = get_available_fields()
    
    assert isinstance(fields, dict)
    assert "id" in fields
    assert "country" in fields
    assert "full_name" in fields
    assert fields == AVAILABLE_FIELDS


@pytest.mark.asyncio
async def test_export_credit_requests_to_excel_success(mock_credit_request):
    """Test exporting credit requests to Excel successfully"""
    with patch('app.services.data_service.search_credit_requests', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([mock_credit_request], 1)
        
        excel_file = await export_credit_requests_to_excel(
            countries=[Country.BRAZIL],
            selected_fields=["id", "country", "full_name", "requested_amount"]
        )
        
        assert isinstance(excel_file, BytesIO)
        assert excel_file.tell() == 0  # File pointer at start
        mock_search.assert_called_once()

