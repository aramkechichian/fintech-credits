"""
Unit tests for LogService with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.log_data import LogDataInDB
from app.services.log_service import log_request, search_logs


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
async def test_log_request_success(mock_log_entry):
    """Test logging a request successfully"""
    with patch('app.services.log_service.log_data_repository.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_log_entry
        
        result = await log_request(
            endpoint="/credit-requests",
            method="POST",
            user_id="507f1f77bcf86cd799439011",
            payload={"test": "data"},
            response_status=201,
            is_success=True
        )
        
        assert result.id == mock_log_entry.id
        assert result.endpoint == "/credit-requests"
        assert result.method == "POST"
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_log_request_without_user_id(mock_log_entry):
    """Test logging a request without user_id"""
    with patch('app.services.log_service.log_data_repository.create', new_callable=AsyncMock) as mock_create:
        mock_log_entry.user_id = None
        mock_create.return_value = mock_log_entry
        
        result = await log_request(
            endpoint="/credit-requests",
            method="GET",
            is_success=True
        )
        
        assert result.user_id is None
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_log_request_sanitizes_password(mock_log_entry):
    """Test that log_request sanitizes sensitive fields"""
    with patch('app.services.log_service.log_data_repository.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_log_entry
        
        await log_request(
            endpoint="/auth/login",
            method="POST",
            payload={"email": "test@example.com", "password": "secret123"},
            is_success=True
        )
        
        # Check that password was sanitized
        call_args = mock_create.call_args[0][0]
        assert call_args.payload["password"] == "***"


@pytest.mark.asyncio
async def test_log_request_error_handling():
    """Test that log_request handles errors gracefully"""
    with patch('app.services.log_service.log_data_repository.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("Database error")
        
        # Should not raise exception, but return a dummy log entry
        result = await log_request(
            endpoint="/credit-requests",
            method="POST",
            is_success=True
        )
        
        assert result is not None
        assert result.endpoint == "/credit-requests"


@pytest.mark.asyncio
async def test_search_logs_success(mock_log_entry):
    """Test searching logs successfully"""
    with patch('app.services.log_service.log_data_repository.search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([mock_log_entry], 1)
        
        results, total = await search_logs(
            method="POST",
            endpoint="/credit-requests",
            skip=0,
            limit=10
        )
        
        assert len(results) == 1
        assert total == 1
        assert results[0].id == mock_log_entry.id
        mock_search.assert_called_once_with(
            method="POST",
            endpoint="/credit-requests",
            date_from=None,
            date_to=None,
            skip=0,
            limit=10
        )


@pytest.mark.asyncio
async def test_search_logs_with_date_range(mock_log_entry):
    """Test searching logs with date range"""
    with patch('app.services.log_service.log_data_repository.search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([mock_log_entry], 1)
        
        date_from = datetime.utcnow() - timedelta(days=7)
        date_to = datetime.utcnow()
        
        results, total = await search_logs(
            date_from=date_from,
            date_to=date_to,
            skip=0,
            limit=10
        )
        
        assert len(results) == 1
        assert total == 1
        mock_search.assert_called_once_with(
            method=None,
            endpoint=None,
            date_from=date_from,
            date_to=date_to,
            skip=0,
            limit=10
        )


@pytest.mark.asyncio
async def test_search_logs_empty_results():
    """Test searching logs with no results"""
    with patch('app.services.log_service.log_data_repository.search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([], 0)
        
        results, total = await search_logs()
        
        assert len(results) == 0
        assert total == 0
