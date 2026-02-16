"""
Unit tests for LogExportService with mocks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from bson import ObjectId
from io import BytesIO
from app.models.log_data import LogDataInDB
from app.services.log_export_service import (
    export_logs_to_excel,
    get_available_fields,
    AVAILABLE_FIELDS
)


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
async def test_get_available_fields():
    """Test getting available fields for export"""
    fields = get_available_fields()
    
    assert isinstance(fields, dict)
    assert "id" in fields
    assert "endpoint" in fields
    assert "module" in fields
    assert "method" in fields
    assert fields == AVAILABLE_FIELDS


@pytest.mark.asyncio
async def test_export_logs_to_excel_success(mock_log_entry):
    """Test exporting logs to Excel successfully"""
    with patch('app.services.log_export_service.log_data_repository.search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([mock_log_entry], 1)
        
        excel_file = await export_logs_to_excel(
            method="POST",
            selected_fields=["id", "endpoint", "method", "response_status"]
        )
        
        assert isinstance(excel_file, BytesIO)
        assert excel_file.tell() == 0  # File pointer at start
        mock_search.assert_called_once()


@pytest.mark.asyncio
async def test_export_logs_to_excel_all_fields(mock_log_entry):
    """Test exporting logs with all fields"""
    with patch('app.services.log_export_service.log_data_repository.search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([mock_log_entry], 1)
        
        excel_file = await export_logs_to_excel(
            selected_fields=None  # Should use all fields
        )
        
        assert isinstance(excel_file, BytesIO)
        mock_search.assert_called_once()


@pytest.mark.asyncio
async def test_export_logs_to_excel_no_data():
    """Test exporting logs when no data found"""
    with patch('app.services.log_export_service.log_data_repository.search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([], 0)
        
        with pytest.raises(ValueError, match="No data found"):
            await export_logs_to_excel()


@pytest.mark.asyncio
async def test_export_logs_to_excel_invalid_fields(mock_log_entry):
    """Test exporting logs with invalid fields"""
    with patch('app.services.log_export_service.log_data_repository.search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([mock_log_entry], 1)
        
        with pytest.raises(ValueError, match="No valid fields selected"):
            await export_logs_to_excel(selected_fields=["invalid_field"])


@pytest.mark.asyncio
async def test_export_logs_to_excel_with_filters(mock_log_entry):
    """Test exporting logs with filters"""
    with patch('app.services.log_export_service.log_data_repository.search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([mock_log_entry], 1)
        
        date_from = datetime.utcnow()
        date_to = datetime.utcnow()
        
        excel_file = await export_logs_to_excel(
            method="POST",
            endpoint="/credit-requests",
            date_from=date_from,
            date_to=date_to,
            selected_fields=["id", "endpoint"]
        )
        
        assert isinstance(excel_file, BytesIO)
        mock_search.assert_called_once_with(
            method="POST",
            endpoint="/credit-requests",
            date_from=date_from,
            date_to=date_to,
            skip=0,
            limit=10000
        )


@pytest.mark.asyncio
async def test_export_logs_to_excel_module_field(mock_log_entry):
    """Test exporting logs with module field"""
    with patch('app.services.log_export_service.log_data_repository.search', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = ([mock_log_entry], 1)
        
        excel_file = await export_logs_to_excel(
            selected_fields=["id", "module", "endpoint"]
        )
        
        assert isinstance(excel_file, BytesIO)
        # Verify the file can be read
        excel_file.seek(0)
        content = excel_file.read()
        assert len(content) > 0
