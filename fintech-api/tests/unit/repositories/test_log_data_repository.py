"""
Unit tests for LogDataRepository with mocks
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.log_data import LogDataInDB
from app.repositories.log_data_repository import LogDataRepository


@pytest.fixture
def mock_database():
    """Mock database connection"""
    db = MagicMock()
    collection = AsyncMock()
    db.__getitem__ = MagicMock(return_value=collection)
    return db, collection


@pytest.fixture
def repository():
    """Create repository instance"""
    return LogDataRepository()


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
async def test_create_log_entry(repository, mock_log_entry, mock_database):
    """Test creating a log entry"""
    db, collection = mock_database
    
    with patch('app.repositories.log_data_repository.get_database', return_value=db):
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = mock_log_entry.id
        collection.insert_one = AsyncMock(return_value=mock_insert_result)
        
        result = await repository.create(mock_log_entry)
        
        assert result.id == mock_log_entry.id
        collection.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id(repository, mock_log_entry, mock_database):
    """Test getting a log entry by ID"""
    db, collection = mock_database
    
    with patch('app.repositories.log_data_repository.get_database', return_value=db):
        log_dict = mock_log_entry.model_dump(by_alias=True)
        collection.find_one = AsyncMock(return_value=log_dict)
        
        result = await repository.get_by_id(str(mock_log_entry.id))
        
        assert result is not None
        assert result.id == mock_log_entry.id
        assert result.endpoint == "/credit-requests"
        collection.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository, mock_database):
    """Test getting a log entry by ID when not found"""
    db, collection = mock_database
    
    with patch('app.repositories.log_data_repository.get_database', return_value=db):
        collection.find_one = AsyncMock(return_value=None)
        
        result = await repository.get_by_id("507f1f77bcf86cd799439012")
        
        assert result is None

