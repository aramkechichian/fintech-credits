"""
Unit tests for CountryRuleRepository with mocks
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from bson import ObjectId
from app.models.country_rule import (
    CountryRuleInDB,
    ValidationRule
)
from app.models.credit_request import Country
from app.repositories.country_rule_repository import CountryRuleRepository


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
    return CountryRuleRepository()


@pytest.fixture
def mock_country_rule():
    """Create a mock country rule"""
    return CountryRuleInDB(
        id=ObjectId("507f1f77bcf86cd799439012"),
        country=Country.SPAIN,
        required_document_type="DNI",
        description="Test rule",
        is_active=True,
        validation_rules=[
            ValidationRule(
                max_percentage=30.0,
                enabled=True,
                error_message="Test error"
            )
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by=ObjectId("507f1f77bcf86cd799439011"),
        updated_by=None
    )


class AsyncIterator:
    """Helper class to create async iterators for mocking"""
    def __init__(self, items):
        self.items = iter(items)
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        try:
            return next(self.items)
        except StopIteration:
            raise StopAsyncIteration


@pytest.mark.asyncio
async def test_create_country_rule(repository, mock_country_rule, mock_database):
    """Test creating a country rule"""
    db, collection = mock_database
    
    # Mock insert_one result
    mock_result = MagicMock()
    mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439012")
    collection.insert_one = AsyncMock(return_value=mock_result)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.create(mock_country_rule)
    
    assert result.id == mock_result.inserted_id
    collection.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_found(repository, mock_country_rule, mock_database):
    """Test getting country rule by ID when found"""
    db, collection = mock_database
    
    rule_doc = {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "country": "Spain",
        "required_document_type": "DNI",
        "description": "Test rule",
        "is_active": True,
        "validation_rules": [
            {
                "max_percentage": 30.0,
                "enabled": True,
                "error_message": "Test error"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": ObjectId("507f1f77bcf86cd799439011"),
        "updated_by": None
    }
    
    collection.find_one = AsyncMock(return_value=rule_doc)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.get_by_id("507f1f77bcf86cd799439012")
    
    assert result is not None
    assert result.country == Country.SPAIN
    assert result.required_document_type == "DNI"
    collection.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(repository, mock_database):
    """Test getting country rule by ID when not found"""
    db, collection = mock_database
    
    collection.find_one = AsyncMock(return_value=None)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.get_by_id("507f1f77bcf86cd799439012")
    
    assert result is None
    collection.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_country_found(repository, mock_country_rule, mock_database):
    """Test getting country rule by country when found"""
    db, collection = mock_database
    
    rule_doc = {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "country": "Spain",
        "required_document_type": "DNI",
        "description": "Test rule",
        "is_active": True,
        "validation_rules": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    collection.find_one = AsyncMock(return_value=rule_doc)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.get_by_country(Country.SPAIN)
    
    assert result is not None
    assert result.country == Country.SPAIN
    collection.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_country_not_found(repository, mock_database):
    """Test getting country rule by country when not found"""
    db, collection = mock_database
    
    collection.find_one = AsyncMock(return_value=None)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.get_by_country(Country.SPAIN)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_all(repository, mock_country_rule, mock_database):
    """Test getting all country rules"""
    db, collection = mock_database
    
    rule_doc = {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "country": "Spain",
        "required_document_type": "DNI",
        "description": "Test rule",
        "is_active": True,
        "validation_rules": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    mock_cursor = MagicMock()
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.__aiter__ = lambda self: AsyncIterator([rule_doc])
    
    collection.find = MagicMock(return_value=mock_cursor)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.get_all(skip=0, limit=100)
    
    assert len(result) == 1
    assert result[0].country == Country.SPAIN


@pytest.mark.asyncio
async def test_update_country_rule(repository, mock_country_rule, mock_database):
    """Test updating a country rule"""
    db, collection = mock_database
    
    update_data = {
        "description": "Updated description",
        "updated_at": datetime.utcnow()
    }
    
    updated_rule_doc = {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "country": "Spain",
        "required_document_type": "DNI",
        "description": "Updated description",
        "is_active": True,
        "validation_rules": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    mock_update_result = MagicMock()
    mock_update_result.modified_count = 1
    collection.update_one = AsyncMock(return_value=mock_update_result)
    collection.find_one = AsyncMock(return_value=updated_rule_doc)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.update("507f1f77bcf86cd799439012", update_data, None)
    
    assert result is not None
    assert result.description == "Updated description"
    collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_delete_country_rule(repository, mock_database):
    """Test deleting a country rule (soft delete)"""
    db, collection = mock_database
    
    mock_delete_result = MagicMock()
    mock_delete_result.modified_count = 1
    collection.update_one = AsyncMock(return_value=mock_delete_result)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.delete("507f1f77bcf86cd799439012")
    
    assert result is True
    collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_hard_delete_country_rule(repository, mock_database):
    """Test hard deleting a country rule"""
    db, collection = mock_database
    
    mock_delete_result = MagicMock()
    mock_delete_result.deleted_count = 1
    collection.delete_one = AsyncMock(return_value=mock_delete_result)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.hard_delete("507f1f77bcf86cd799439012")
    
    assert result is True
    collection.delete_one.assert_called_once()


@pytest.mark.asyncio
async def test_count_country_rules(repository, mock_database):
    """Test counting country rules"""
    db, collection = mock_database
    
    collection.count_documents = AsyncMock(return_value=5)
    
    with patch('app.repositories.country_rule_repository.get_database', return_value=db):
        result = await repository.count(is_active=True)
    
    assert result == 5
    collection.count_documents.assert_called_once()
