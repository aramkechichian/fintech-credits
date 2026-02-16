"""
Unit tests for BankProviderController with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from datetime import datetime
from bson import ObjectId
from app.models.credit_request import Country
from app.models.user import UserInDB
from app.controllers import bank_provider_controller


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


@pytest.mark.asyncio
async def test_get_bank_information_success(mock_user):
    """Test getting bank information successfully"""
    mock_response = {
        "status": "not_connected",
        "message": "No existe ninguna API externa conectada para el país Brazil.",
        "description": "Este challenge deja preparada la posibilidad...",
        "country": "Brazil",
        "full_name": "John Doe",
        "identity_document": "123.456.789-09",
        "bank_information": None
    }
    
    with patch('app.controllers.bank_provider_controller.get_bank_information', new_callable=AsyncMock) as mock_get_info:
        mock_get_info.return_value = mock_response
        
        result = await bank_provider_controller.get_bank_information_endpoint(
            country="Brazil",
            full_name="John Doe",
            identity_document="123.456.789-09",
            current_user=mock_user
        )
    
    assert result.status_code == 200
    content = result.body.decode('utf-8')
    import json
    data = json.loads(content)
    assert data["status"] == "not_connected"
    assert data["country"] == "Brazil"
    mock_get_info.assert_called_once()


@pytest.mark.asyncio
async def test_get_bank_information_invalid_country(mock_user):
    """Test getting bank information with invalid country"""
    with pytest.raises(HTTPException) as exc_info:
        await bank_provider_controller.get_bank_information_endpoint(
            country="InvalidCountry",
            full_name="John Doe",
            identity_document="123456789",
            current_user=mock_user
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid country" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_bank_information_empty_full_name(mock_user):
    """Test getting bank information with empty full name"""
    with pytest.raises(HTTPException) as exc_info:
        await bank_provider_controller.get_bank_information_endpoint(
            country="Brazil",
            full_name="",
            identity_document="123456789",
            current_user=mock_user
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Full name is required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_bank_information_empty_identity_document(mock_user):
    """Test getting bank information with empty identity document"""
    with pytest.raises(HTTPException) as exc_info:
        await bank_provider_controller.get_bank_information_endpoint(
            country="Brazil",
            full_name="John Doe",
            identity_document="",
            current_user=mock_user
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Identity document is required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_bank_information_whitespace_only_full_name(mock_user):
    """Test getting bank information with whitespace-only full name"""
    with pytest.raises(HTTPException) as exc_info:
        await bank_provider_controller.get_bank_information_endpoint(
            country="Brazil",
            full_name="   ",
            identity_document="123456789",
            current_user=mock_user
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Full name is required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_bank_information_whitespace_only_identity_document(mock_user):
    """Test getting bank information with whitespace-only identity document"""
    with pytest.raises(HTTPException) as exc_info:
        await bank_provider_controller.get_bank_information_endpoint(
            country="Brazil",
            full_name="John Doe",
            identity_document="   ",
            current_user=mock_user
        )
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Identity document is required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_bank_information_all_countries(mock_user):
    """Test getting bank information for all valid countries"""
    countries = ["Brazil", "Mexico", "Spain", "Portugal", "Italy", "Colombia"]
    
    for country in countries:
        mock_response = {
            "status": "not_connected",
            "message": f"No existe ninguna API externa conectada para el país {country}.",
            "country": country,
            "full_name": "Test User",
            "identity_document": "123456789",
            "bank_information": None
        }
        
        with patch('app.controllers.bank_provider_controller.get_bank_information', new_callable=AsyncMock) as mock_get_info:
            mock_get_info.return_value = mock_response
            
            result = await bank_provider_controller.get_bank_information_endpoint(
                country=country,
                full_name="Test User",
                identity_document="123456789",
                current_user=mock_user
            )
        
        assert result.status_code == 200
        import json
        data = json.loads(result.body.decode('utf-8'))
        assert data["country"] == country


@pytest.mark.asyncio
async def test_get_bank_information_service_error(mock_user):
    """Test handling service errors"""
    with patch('app.controllers.bank_provider_controller.get_bank_information', new_callable=AsyncMock) as mock_get_info:
        mock_get_info.side_effect = Exception("Service error")
        
        with pytest.raises(HTTPException) as exc_info:
            await bank_provider_controller.get_bank_information_endpoint(
                country="Brazil",
                full_name="John Doe",
                identity_document="123456789",
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error retrieving bank information" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_bank_information_trims_inputs(mock_user):
    """Test that inputs are trimmed before processing"""
    mock_response = {
        "status": "not_connected",
        "country": "Brazil",
        "full_name": "John Doe",
        "identity_document": "123456789",
        "bank_information": None
    }
    
    with patch('app.controllers.bank_provider_controller.get_bank_information', new_callable=AsyncMock) as mock_get_info:
        mock_get_info.return_value = mock_response
        
        result = await bank_provider_controller.get_bank_information_endpoint(
            country="Brazil",
            full_name="  John Doe  ",
            identity_document="  123456789  ",
            current_user=mock_user
        )
    
    # Verify that trimmed values are passed to service
    call_args = mock_get_info.call_args
    assert call_args[1]["full_name"] == "John Doe"  # Should be trimmed
    assert call_args[1]["identity_document"] == "123456789"  # Should be trimmed
