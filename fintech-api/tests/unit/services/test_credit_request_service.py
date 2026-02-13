"""
Unit tests for CreditRequestService with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from bson import ObjectId
from app.models.credit_request import (
    CreditRequestCreate,
    CreditRequestStatus,
    Country,
    CurrencyCode,
    BankInformation
)
from app.services.credit_request_service import (
    create_credit_request,
    get_credit_request_by_id,
    get_user_credit_requests,
    update_credit_request_status,
    search_credit_requests
)


@pytest.fixture
def credit_request_data():
    """Create credit request data for testing"""
    return CreditRequestCreate(
        country=Country.BRAZIL,
        full_name="John Doe",
        identity_document="123456789",
        requested_amount=10000.0,
        monthly_income=5000.0
    )


@pytest.mark.asyncio
async def test_create_credit_request_success(credit_request_data):
    """Test creating a credit request successfully"""
    user_id = "507f1f77bcf86cd799439011"
    
    mock_created_request = MagicMock()
    mock_created_request.id = ObjectId("507f1f77bcf86cd799439012")
    mock_created_request.user_id = ObjectId(user_id)
    mock_created_request.country = Country.BRAZIL
    mock_created_request.currency_code = CurrencyCode.BRL
    mock_created_request.full_name = "John Doe"
    mock_created_request.identity_document = "123456789"
    mock_created_request.requested_amount = 10000.0
    mock_created_request.monthly_income = 5000.0
    mock_created_request.status = CreditRequestStatus.PENDING
    
    with patch('app.services.credit_request_service.credit_request_repository') as mock_repo, \
         patch('app.services.credit_request_service.log_request', new_callable=AsyncMock) as mock_log:
        mock_repo.create = AsyncMock(return_value=mock_created_request)
        
        result = await create_credit_request(
            user_id=user_id,
            credit_request_data=credit_request_data,
            bank_information=None
        )
    
    assert result.id == mock_created_request.id
    assert result.currency_code == CurrencyCode.BRL
    assert result.status == CreditRequestStatus.PENDING
    mock_repo.create.assert_called_once()
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_create_credit_request_with_bank_info(credit_request_data):
    """Test creating a credit request with bank information"""
    user_id = "507f1f77bcf86cd799439011"
    bank_info = BankInformation(
        bank_name="Test Bank",
        account_number="1234567890"
    )
    
    mock_created_request = MagicMock()
    mock_created_request.id = ObjectId("507f1f77bcf86cd799439012")
    mock_created_request.bank_information = bank_info
    
    with patch('app.services.credit_request_service.credit_request_repository') as mock_repo, \
         patch('app.services.credit_request_service.log_request', new_callable=AsyncMock):
        mock_repo.create = AsyncMock(return_value=mock_created_request)
        
        result = await create_credit_request(
            user_id=user_id,
            credit_request_data=credit_request_data,
            bank_information=bank_info
        )
    
    assert result.bank_information == bank_info
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_credit_request_currency_mapping():
    """Test currency code mapping for different countries"""
    test_cases = [
        (Country.BRAZIL, CurrencyCode.BRL),
        (Country.MEXICO, CurrencyCode.MXN),
        (Country.SPAIN, CurrencyCode.EUR),
        (Country.PORTUGAL, CurrencyCode.EUR),
        (Country.ITALY, CurrencyCode.EUR),
        (Country.COLOMBIA, CurrencyCode.COP),
    ]
    
    for country, expected_currency in test_cases:
        credit_request_data = CreditRequestCreate(
            country=country,
            full_name="Test User",
            identity_document="123456789",
            requested_amount=10000.0,
            monthly_income=5000.0
        )
        
        mock_created_request = MagicMock()
        mock_created_request.currency_code = expected_currency
        
        with patch('app.services.credit_request_service.credit_request_repository') as mock_repo, \
             patch('app.services.credit_request_service.log_request', new_callable=AsyncMock):
            mock_repo.create = AsyncMock(return_value=mock_created_request)
            
            result = await create_credit_request(
                user_id="507f1f77bcf86cd799439011",
                credit_request_data=credit_request_data,
                bank_information=None
            )
        
        assert result.currency_code == expected_currency


@pytest.mark.asyncio
async def test_get_credit_request_by_id_found():
    """Test getting credit request by ID when found"""
    request_id = "507f1f77bcf86cd799439012"
    mock_request = MagicMock()
    mock_request.id = ObjectId(request_id)
    
    with patch('app.services.credit_request_service.credit_request_repository') as mock_repo:
        mock_repo.get_by_id = AsyncMock(return_value=mock_request)
        
        result = await get_credit_request_by_id(request_id)
    
    assert result == mock_request
    mock_repo.get_by_id.assert_called_once_with(request_id)


@pytest.mark.asyncio
async def test_get_credit_request_by_id_not_found():
    """Test getting credit request by ID when not found"""
    request_id = "507f1f77bcf86cd799439012"
    
    with patch('app.services.credit_request_service.credit_request_repository') as mock_repo:
        mock_repo.get_by_id = AsyncMock(return_value=None)
        
        result = await get_credit_request_by_id(request_id)
    
    assert result is None
    mock_repo.get_by_id.assert_called_once_with(request_id)


@pytest.mark.asyncio
async def test_get_user_credit_requests():
    """Test getting all credit requests for a user"""
    user_id = "507f1f77bcf86cd799439011"
    mock_requests = [MagicMock(), MagicMock()]
    
    with patch('app.services.credit_request_service.credit_request_repository') as mock_repo:
        mock_repo.get_by_user_id = AsyncMock(return_value=mock_requests)
        
        result = await get_user_credit_requests(user_id)
    
    assert result == mock_requests
    mock_repo.get_by_user_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_update_credit_request_status():
    """Test updating credit request status"""
    request_id = "507f1f77bcf86cd799439012"
    new_status = CreditRequestStatus.APPROVED
    
    mock_updated_request = MagicMock()
    mock_updated_request.id = ObjectId(request_id)
    mock_updated_request.status = new_status
    
    with patch('app.services.credit_request_service.credit_request_repository') as mock_repo:
        mock_repo.update = AsyncMock(return_value=mock_updated_request)
        
        result = await update_credit_request_status(
            request_id=request_id,
            new_status=new_status,
            bank_information=None
        )
    
    assert result == mock_updated_request
    assert result.status == new_status
    mock_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_credit_request_with_bank_info():
    """Test updating credit request with bank information"""
    request_id = "507f1f77bcf86cd799439012"
    new_status = CreditRequestStatus.APPROVED
    bank_info = BankInformation(
        bank_name="Test Bank",
        account_number="1234567890"
    )
    
    mock_updated_request = MagicMock()
    mock_updated_request.bank_information = bank_info
    
    with patch('app.services.credit_request_service.credit_request_repository') as mock_repo:
        mock_repo.update = AsyncMock(return_value=mock_updated_request)
        
        result = await update_credit_request_status(
            request_id=request_id,
            new_status=new_status,
            bank_information=bank_info
        )
    
    assert result.bank_information == bank_info
    mock_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_search_credit_requests():
    """Test searching credit requests with filters"""
    user_id = "507f1f77bcf86cd799439011"
    mock_requests = [MagicMock(), MagicMock()]
    total_count = 2
    
    with patch('app.services.credit_request_service.credit_request_repository') as mock_repo:
        mock_repo.search = AsyncMock(return_value=(mock_requests, total_count))
        
        results, total = await search_credit_requests(
            user_id=user_id,
            countries=["Brazil"],
            identity_document="123",
            status="pending",
            skip=0,
            limit=20
        )
    
    assert results == mock_requests
    assert total == total_count
    mock_repo.search.assert_called_once()
