"""
Unit tests for CreditRequestRepository with mocks
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from bson import ObjectId
from app.models.credit_request import (
    CreditRequestInDB,
    CreditRequestStatus,
    Country,
    CurrencyCode
)
from app.repositories.credit_request_repository import CreditRequestRepository


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
    return CreditRequestRepository()


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
async def test_create_credit_request(repository, mock_credit_request, mock_database):
    """Test creating a credit request"""
    db, collection = mock_database
    
    # Mock insert_one result
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439012")
    collection.insert_one = AsyncMock(return_value=mock_result)
    
    with patch('app.repositories.credit_request_repository.get_database', return_value=db):
        result = await repository.create(mock_credit_request)
    
    assert result.id == mock_result.inserted_id
    collection.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_found(repository, mock_credit_request, mock_database):
    """Test getting credit request by ID when found"""
    db, collection = mock_database
    
    request_doc = {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "user_id": ObjectId("507f1f77bcf86cd799439011"),
        "country": "Brazil",
        "currency_code": "BRL",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "identity_document": "123456789",
        "requested_amount": 10000.0,
        "monthly_income": 5000.0,
        "request_date": datetime.utcnow(),
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    collection.find_one = AsyncMock(return_value=request_doc)
    
    with patch('app.repositories.credit_request_repository.get_database', return_value=db):
        result = await repository.get_by_id("507f1f77bcf86cd799439012")
    
    assert result is not None
    assert str(result.id) == "507f1f77bcf86cd799439012"
    collection.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository, mock_database):
    """Test getting credit request by ID when not found"""
    db, collection = mock_database
    
    collection.find_one = AsyncMock(return_value=None)
    
    with patch('app.repositories.credit_request_repository.get_database', return_value=db):
        result = await repository.get_by_id("507f1f77bcf86cd799439012")
    
    assert result is None
    collection.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_update_credit_request(repository, mock_database):
    """Test updating a credit request"""
    db, collection = mock_database
    
    update_data = {"status": CreditRequestStatus.APPROVED}
    
    mock_update_result = MagicMock()
    mock_update_result.modified_count = 1
    collection.update_one = AsyncMock(return_value=mock_update_result)
    
    # Mock get_by_id for the return
    updated_doc = {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "user_id": ObjectId("507f1f77bcf86cd799439011"),
        "country": "Brazil",
        "currency_code": "BRL",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "identity_document": "123456789",
        "requested_amount": 10000.0,
        "monthly_income": 5000.0,
        "request_date": datetime.utcnow(),
        "status": "approved",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    collection.find_one = AsyncMock(return_value=updated_doc)
    
    with patch('app.repositories.credit_request_repository.get_database', return_value=db):
        result = await repository.update("507f1f77bcf86cd799439012", update_data)
    
    assert result is not None
    assert result.status == CreditRequestStatus.APPROVED
    collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_search_credit_requests(repository, mock_database):
    """Test searching credit requests with filters"""
    db, collection = mock_database
    
    request_docs = [
        {
            "_id": ObjectId("507f1f77bcf86cd799439012"),
            "country": "Brazil",
            "currency_code": "BRL",
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "identity_document": "123456789",
            "requested_amount": 10000.0,
            "monthly_income": 5000.0,
            "request_date": datetime.utcnow(),
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    collection.count_documents = AsyncMock(return_value=1)
    
    class AsyncIterator:
        def __init__(self, items):
            self.items = items
        
        def __aiter__(self):
            return self
        
        async def __anext__(self):
            if not self.items:
                raise StopAsyncIteration
            return self.items.pop(0)
    
    async_iterator = AsyncIterator(request_docs.copy())
    mock_cursor = MagicMock()
    mock_cursor.__aiter__ = lambda self: async_iterator
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    
    collection.find = MagicMock(return_value=mock_cursor)
    
    with patch('app.repositories.credit_request_repository.get_database', return_value=db):
        results, total = await repository.search(
            countries=["Brazil"],
            status="pending",
            skip=0,
            limit=20
        )
    
    assert len(results) == 1
    assert total == 1
    collection.count_documents.assert_called_once()


@pytest.mark.asyncio
async def test_delete_credit_request(repository, mock_database):
    """Test deleting a credit request"""
    db, collection = mock_database
    
    mock_delete_result = MagicMock()
    mock_delete_result.deleted_count = 1
    collection.delete_one = AsyncMock(return_value=mock_delete_result)
    
    with patch('app.repositories.credit_request_repository.get_database', return_value=db):
        result = await repository.delete("507f1f77bcf86cd799439012")
    
    assert result is True
    collection.delete_one.assert_called_once()
