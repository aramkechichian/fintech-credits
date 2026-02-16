"""
Unit tests for CreditRequestController with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from datetime import datetime
from bson import ObjectId
from app.models.credit_request import (
    CreditRequestCreate,
    CreditRequestResponse,
    CreditRequestStatus,
    CreditRequestUpdate,
    Country,
    CurrencyCode
)
from app.models.user import UserInDB
from app.controllers import credit_request_controller


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
def credit_request_data():
    """Create credit request data"""
    return CreditRequestCreate(
        country=Country.BRAZIL,
        full_name="John Doe",
        identity_document="123456789",
        requested_amount=10000.0,
        monthly_income=5000.0
    )


@pytest.fixture
def mock_credit_request():
    """Create a mock credit request"""
    from app.models.credit_request import CreditRequestInDB
    return CreditRequestInDB(
        id=ObjectId("507f1f77bcf86cd799439012"),
        user_id=ObjectId("507f1f77bcf86cd799439011"),
        country=Country.BRAZIL,
        currency_code=CurrencyCode.BRL,
        full_name="John Doe",
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
async def test_create_request_success(credit_request_data, mock_user, mock_credit_request):
    """Test creating a credit request successfully"""
    with patch('app.controllers.credit_request_controller.create_credit_request', new_callable=AsyncMock) as mock_create, \
         patch('app.controllers.credit_request_controller.log_request', new_callable=AsyncMock) as mock_log:
        mock_create.return_value = mock_credit_request
        
        result = await credit_request_controller.create_request(
            credit_request_data=credit_request_data,
            current_user=mock_user
        )
    
    assert isinstance(result, CreditRequestResponse)
    assert result.id == str(mock_credit_request.id)
    assert result.country == Country.BRAZIL
    mock_create.assert_called_once()
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_create_request_validation_error(credit_request_data, mock_user):
    """Test creating a credit request with validation error"""
    with patch('app.controllers.credit_request_controller.create_credit_request', new_callable=AsyncMock) as mock_create, \
         patch('app.controllers.credit_request_controller.log_request', new_callable=AsyncMock) as mock_log:
        mock_create.side_effect = ValueError("Invalid country")
        
        with pytest.raises(HTTPException) as exc_info:
            await credit_request_controller.create_request(
                credit_request_data=credit_request_data,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_get_my_requests_success(mock_user, mock_credit_request):
    """Test getting all credit requests for current user"""
    mock_requests = [mock_credit_request]
    
    with patch('app.controllers.credit_request_controller.get_user_credit_requests', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_requests
        
        result = await credit_request_controller.get_my_requests(current_user=mock_user)
    
    assert len(result) == 1
    assert isinstance(result[0], CreditRequestResponse)
    mock_get.assert_called_once_with(str(mock_user.id))


@pytest.mark.asyncio
async def test_get_my_requests_empty(mock_user):
    """Test getting credit requests when user has none"""
    with patch('app.controllers.credit_request_controller.get_user_credit_requests', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        
        result = await credit_request_controller.get_my_requests(current_user=mock_user)
    
    assert len(result) == 0
    mock_get.assert_called_once_with(str(mock_user.id))


@pytest.mark.asyncio
async def test_get_request_success(mock_user, mock_credit_request):
    """Test getting a specific credit request"""
    request_id = "507f1f77bcf86cd799439012"
    
    with patch('app.controllers.credit_request_controller.get_credit_request_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_credit_request
        
        result = await credit_request_controller.get_request(
            request_id=request_id,
            current_user=mock_user
        )
    
    assert isinstance(result, CreditRequestResponse)
    assert result.id == request_id
    mock_get.assert_called_once_with(request_id)


@pytest.mark.asyncio
async def test_get_request_not_found(mock_user):
    """Test getting a credit request that doesn't exist"""
    request_id = "507f1f77bcf86cd799439012"
    
    with patch('app.controllers.credit_request_controller.get_credit_request_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await credit_request_controller.get_request(
                request_id=request_id,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_request_forbidden(mock_user, mock_credit_request):
    """Test getting a credit request that belongs to another user"""
    request_id = "507f1f77bcf86cd799439012"
    # Change user_id to a different user
    mock_credit_request.user_id = ObjectId("507f1f77bcf86cd799439099")
    
    with patch('app.controllers.credit_request_controller.get_credit_request_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_credit_request
        
        with pytest.raises(HTTPException) as exc_info:
            await credit_request_controller.get_request(
                request_id=request_id,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_update_request_success(mock_user, mock_credit_request):
    """Test updating a credit request status"""
    request_id = "507f1f77bcf86cd799439012"
    update_data = CreditRequestUpdate(status=CreditRequestStatus.APPROVED)
    
    # Create updated request
    updated_request = mock_credit_request
    updated_request.status = CreditRequestStatus.APPROVED
    
    with patch('app.controllers.credit_request_controller.get_credit_request_by_id', new_callable=AsyncMock) as mock_get, \
         patch('app.controllers.credit_request_controller.update_credit_request_status', new_callable=AsyncMock) as mock_update, \
         patch('app.controllers.credit_request_controller.log_request', new_callable=AsyncMock) as mock_log:
        mock_get.return_value = mock_credit_request
        mock_update.return_value = updated_request
        
        result = await credit_request_controller.update_request(
            request_id=request_id,
            update_data=update_data,
            current_user=mock_user
        )
    
    # JSONResponse returns status_code in the response object
    assert hasattr(result, 'status_code') and result.status_code == 200
    mock_get.assert_called_once_with(request_id)
    mock_update.assert_called_once()
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_update_request_not_found(mock_user):
    """Test updating a credit request that doesn't exist"""
    request_id = "507f1f77bcf86cd799439012"
    update_data = CreditRequestUpdate(status=CreditRequestStatus.APPROVED)
    
    with patch('app.controllers.credit_request_controller.get_credit_request_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await credit_request_controller.update_request(
                request_id=request_id,
                update_data=update_data,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_request_forbidden(mock_user, mock_credit_request):
    """Test updating a credit request that belongs to another user"""
    request_id = "507f1f77bcf86cd799439012"
    update_data = CreditRequestUpdate(status=CreditRequestStatus.APPROVED)
    # Change user_id to a different user
    mock_credit_request.user_id = ObjectId("507f1f77bcf86cd799439099")
    
    with patch('app.controllers.credit_request_controller.get_credit_request_by_id', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_credit_request
        
        with pytest.raises(HTTPException) as exc_info:
            await credit_request_controller.update_request(
                request_id=request_id,
                update_data=update_data,
                current_user=mock_user
            )
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_search_requests_success(mock_user, mock_credit_request):
    """Test searching credit requests with filters"""
    mock_requests = [mock_credit_request]
    total_count = 1
    
    with patch('app.controllers.credit_request_controller.search_credit_requests', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = (mock_requests, total_count)
        
        result = await credit_request_controller.search_requests(
            current_user=mock_user,
            countries=["Brazil"],
            identity_document="123",
            status_filter="pending",
            page=1,
            limit=20
        )
    
    assert result["total"] == total_count
    assert len(result["items"]) == 1
    assert result["page"] == 1
    assert result["limit"] == 20
    mock_search.assert_called_once()
    # Note: log_request was removed from search endpoint


@pytest.mark.asyncio
async def test_search_requests_empty(mock_user):
    """Test searching credit requests with no results"""
    with patch('app.controllers.credit_request_controller.search_credit_requests', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([], 0)
        
        result = await credit_request_controller.search_requests(
            current_user=mock_user,
            countries=None,
            identity_document=None,
            status_filter=None,
            page=1,
            limit=20
        )
    
    assert result["total"] == 0
    assert len(result["items"]) == 0
    mock_search.assert_called_once()
    # Note: log_request was removed from search endpoint
