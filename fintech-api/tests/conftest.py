"""
Pytest configuration and shared fixtures
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from bson import ObjectId
from app.models.credit_request import (
    CreditRequestInDB,
    CreditRequestStatus,
    Country,
    CurrencyCode,
    BankInformation
)
from app.models.user import UserInDB


@pytest.fixture
def mock_user():
    """Create a mock user for testing"""
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
    """Create a mock credit request for testing"""
    return CreditRequestInDB(
        id=ObjectId("507f1f77bcf86cd799439012"),
        user_id=ObjectId("507f1f77bcf86cd799439011"),
        country=Country.BRAZIL,
        currency_code=CurrencyCode.BRL,
        full_name="John Rambo",
        identity_document="123456789",
        requested_amount=10000.0,
        monthly_income=5000.0,
        request_date=datetime.utcnow(),
        status=CreditRequestStatus.PENDING,
        bank_information=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_credit_request_approved():
    """Create a mock approved credit request"""
    return CreditRequestInDB(
        id=ObjectId("507f1f77bcf86cd799439013"),
        user_id=ObjectId("507f1f77bcf86cd799439011"),
        country=Country.SPAIN,
        currency_code=CurrencyCode.EUR,
        full_name="Rocky Balboa",
        identity_document="987654321",
        requested_amount=20000.0,
        monthly_income=8000.0,
        request_date=datetime.utcnow(),
        status=CreditRequestStatus.APPROVED,
        bank_information=BankInformation(
            bank_name="Test Bank",
            account_number="1234567890"
        ),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_get_current_user(mock_user):
    """Mock dependency for get_current_user"""
    async def _mock_get_current_user():
        return mock_user
    return _mock_get_current_user
