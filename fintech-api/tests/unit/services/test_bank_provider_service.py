"""
Unit tests for BankProviderService with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.credit_request import Country
from app.services.bank_provider_service import (
    get_bank_information,
    fetch_bank_information_from_provider
)


@pytest.mark.asyncio
async def test_get_bank_information_not_connected():
    """Test getting bank information when no API is connected"""
    country = Country.BRAZIL
    full_name = "John Doe"
    identity_document = "123.456.789-09"
    
    result = await get_bank_information(
        country=country,
        full_name=full_name,
        identity_document=identity_document
    )
    
    assert result["status"] == "not_connected"
    assert "No existe ninguna API externa conectada" in result["message"]
    assert result["country"] == "Brazil"
    assert result["full_name"] == full_name
    assert result["identity_document"] == identity_document
    assert result["bank_information"] is None
    assert "description" in result
    assert "challenge" in result["description"].lower() or "arquitectura" in result["description"].lower()


@pytest.mark.asyncio
async def test_get_bank_information_all_countries():
    """Test getting bank information for all countries"""
    test_cases = [
        Country.BRAZIL,
        Country.MEXICO,
        Country.SPAIN,
        Country.PORTUGAL,
        Country.ITALY,
        Country.COLOMBIA,
    ]
    
    for country in test_cases:
        result = await get_bank_information(
            country=country,
            full_name="Test User",
            identity_document="123456789"
        )
        
        assert result["status"] == "not_connected"
        assert result["country"] == country.value
        assert "No existe ninguna API externa conectada" in result["message"]
        assert result["bank_information"] is None


@pytest.mark.asyncio
async def test_get_bank_information_message_includes_country():
    """Test that the message includes the country name"""
    country = Country.MEXICO
    result = await get_bank_information(
        country=country,
        full_name="Test User",
        identity_document="ABCD123456HDFXYZ01"
    )
    
    assert country.value in result["message"]
    assert "México" in result["message"] or "Mexico" in result["message"]


@pytest.mark.asyncio
async def test_fetch_bank_information_from_provider_not_connected():
    """Test fetching bank information when provider is not connected"""
    country = Country.SPAIN
    identity_document = "12345678Z"
    full_name = "John Doe"
    
    result = await fetch_bank_information_from_provider(
        country=country,
        identity_document=identity_document,
        full_name=full_name
    )
    
    # Should return None when provider is not connected
    assert result is None


@pytest.mark.asyncio
async def test_fetch_bank_information_from_provider_without_full_name():
    """Test fetching bank information without full name"""
    country = Country.COLOMBIA
    identity_document = "12345678"
    
    result = await fetch_bank_information_from_provider(
        country=country,
        identity_document=identity_document,
        full_name=None
    )
    
    # Should return None when provider is not connected
    assert result is None


@pytest.mark.asyncio
async def test_get_bank_information_preserves_inputs():
    """Test that input values are preserved in the response"""
    country = Country.ITALY
    full_name = "Mario Rossi"
    identity_document = "RSSMRA80A01H501U"
    
    result = await get_bank_information(
        country=country,
        full_name=full_name,
        identity_document=identity_document
    )
    
    assert result["full_name"] == full_name
    assert result["identity_document"] == identity_document
    assert result["country"] == country.value


@pytest.mark.asyncio
async def test_get_bank_information_description_present():
    """Test that description about challenge is present"""
    result = await get_bank_information(
        country=Country.PORTUGAL,
        full_name="Test",
        identity_document="123456789"
    )
    
    assert "description" in result
    assert len(result["description"]) > 0
    # Should mention that architecture is prepared
    description_lower = result["description"].lower()
    assert "challenge" in description_lower or "arquitectura" in description_lower or "preparada" in description_lower
