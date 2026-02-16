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
    get_all_credit_requests,
    update_credit_request_status,
    search_credit_requests,
    validate_country_rules,
    ValidationError
)
from app.models.country_rule import CountryRuleInDB, ValidationRule


@pytest.fixture
def credit_request_data():
    """Create credit request data for testing"""
    return CreditRequestCreate(
        country=Country.BRAZIL,
        full_name="John Doe",
        email="john.doe@example.com",
        identity_document="123456789",
        requested_amount=10000.0,
        monthly_income=5000.0
    )


@pytest.mark.asyncio
async def test_create_credit_request_success(credit_request_data):
    """Test creating a credit request successfully"""
    mock_created_request = MagicMock()
    mock_created_request.id = ObjectId("507f1f77bcf86cd799439012")
    mock_created_request.country = Country.BRAZIL
    mock_created_request.currency_code = CurrencyCode.BRL
    mock_created_request.full_name = "John Doe"
    mock_created_request.identity_document = "123456789"
    mock_created_request.requested_amount = 10000.0
    mock_created_request.monthly_income = 5000.0
    mock_created_request.status = CreditRequestStatus.PENDING
    
    with patch('app.services.credit_request_service.get_country_rule_by_country', new_callable=AsyncMock) as mock_get_rule, \
         patch('app.services.credit_request_service.credit_request_repository') as mock_repo, \
         patch('app.services.credit_request_service.log_request', new_callable=AsyncMock) as mock_log:
        # Mock no country rule found (validation passes)
        mock_get_rule.return_value = None
        mock_repo.create = AsyncMock(return_value=mock_created_request)
        
        result = await create_credit_request(
            credit_request_data=credit_request_data,
            bank_information=None
        )
    
    assert result.id == mock_created_request.id
    assert result.currency_code == CurrencyCode.BRL
    assert result.status == CreditRequestStatus.PENDING
    mock_repo.create.assert_called_once()


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
    
    with patch('app.services.credit_request_service.get_country_rule_by_country', new_callable=AsyncMock) as mock_get_rule, \
         patch('app.services.credit_request_service.credit_request_repository') as mock_repo, \
         patch('app.services.credit_request_service.log_request', new_callable=AsyncMock):
        # Mock no country rule found (validation passes)
        mock_get_rule.return_value = None
        mock_repo.create = AsyncMock(return_value=mock_created_request)
        
        result = await create_credit_request(
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
            email="test@example.com",
            identity_document="123456789",
            requested_amount=10000.0,
            monthly_income=5000.0
        )
        
        mock_created_request = MagicMock()
        mock_created_request.currency_code = expected_currency
        
        with patch('app.services.credit_request_service.get_country_rule_by_country', new_callable=AsyncMock) as mock_get_rule, \
             patch('app.services.credit_request_service.credit_request_repository') as mock_repo, \
             patch('app.services.credit_request_service.log_request', new_callable=AsyncMock):
            # Mock no country rule found (validation passes)
            mock_get_rule.return_value = None
            mock_repo.create = AsyncMock(return_value=mock_created_request)
            
            result = await create_credit_request(
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
async def test_get_all_credit_requests():
    """Test getting all credit requests"""
    mock_requests = [MagicMock(), MagicMock()]
    
    with patch('app.services.credit_request_service.credit_request_repository') as mock_repo:
        mock_repo.get_all = AsyncMock(return_value=mock_requests)
        
        result = await get_all_credit_requests()
    
    assert result == mock_requests
    mock_repo.get_all.assert_called_once()


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
            countries=["Brazil"],
            identity_document="123",
            status="pending",
            skip=0,
            limit=20
        )
    
    assert results == mock_requests
    assert total == total_count
    mock_repo.search.assert_called_once()


# Tests for country rules validation
@pytest.fixture
def mock_country_rule():
    """Create a mock country rule for testing"""
    return CountryRuleInDB(
        country=Country.BRAZIL,
        required_document_type="CPF",
        description="Test rule",
        is_active=True,
        validation_rules=[
            ValidationRule(
                max_percentage=30.0,
                enabled=True,
                error_message="El monto solicitado no puede exceder el 30% del ingreso mensual"
            )
        ]
    )


@pytest.mark.asyncio
async def test_validate_country_rules_success(mock_country_rule):
    """Test successful country rules validation"""
    with patch('app.services.credit_request_service.get_country_rule_by_country', new_callable=AsyncMock) as mock_get_rule:
        mock_get_rule.return_value = mock_country_rule
        
        # Valid CPF and valid percentage (20% of income)
        await validate_country_rules(
            country=Country.BRAZIL,
            identity_document="123.456.789-09",
            requested_amount=1000.0,  # 20% of 5000
            monthly_income=5000.0
        )
        
        # Should not raise any exception
        mock_get_rule.assert_called_once_with(Country.BRAZIL)


@pytest.mark.asyncio
async def test_validate_country_rules_no_rule_found():
    """Test validation when no country rule exists (should pass)"""
    with patch('app.services.credit_request_service.get_country_rule_by_country', new_callable=AsyncMock) as mock_get_rule:
        mock_get_rule.return_value = None
        
        # Should not raise exception when no rule exists
        await validate_country_rules(
            country=Country.BRAZIL,
            identity_document="123.456.789-09",
            requested_amount=10000.0,
            monthly_income=5000.0
        )


@pytest.mark.asyncio
async def test_validate_country_rules_inactive_rule(mock_country_rule):
    """Test validation when country rule is inactive (should pass)"""
    mock_country_rule.is_active = False
    
    with patch('app.services.credit_request_service.get_country_rule_by_country', new_callable=AsyncMock) as mock_get_rule:
        mock_get_rule.return_value = mock_country_rule
        
        # Should not raise exception when rule is inactive
        await validate_country_rules(
            country=Country.BRAZIL,
            identity_document="123.456.789-09",
            requested_amount=10000.0,
            monthly_income=5000.0
        )


@pytest.mark.asyncio
async def test_validate_country_rules_invalid_document_format(mock_country_rule):
    """Test validation failure due to invalid document format"""
    with patch('app.services.credit_request_service.get_country_rule_by_country', new_callable=AsyncMock) as mock_get_rule:
        mock_get_rule.return_value = mock_country_rule
        
        # Invalid CPF format
        with pytest.raises(ValidationError) as exc_info:
            await validate_country_rules(
                country=Country.BRAZIL,
                identity_document="123456",  # Invalid CPF
                requested_amount=1000.0,
                monthly_income=5000.0
            )
        
        error_details = exc_info.value.rule_details
        assert "errors" in error_details
        assert len(error_details["errors"]) > 0
        assert error_details["errors"][0].get("rule_type") == "document_format"
        assert exc_info.value.message == "La solicitud no cumple con las reglas de validación del país"


@pytest.mark.asyncio
async def test_validate_country_rules_exceeds_percentage(mock_country_rule):
    """Test validation failure due to exceeding max percentage"""
    with patch('app.services.credit_request_service.get_country_rule_by_country', new_callable=AsyncMock) as mock_get_rule:
        mock_get_rule.return_value = mock_country_rule
        
        # Requested amount is 40% of income (exceeds 30% max)
        with pytest.raises(ValidationError) as exc_info:
            await validate_country_rules(
                country=Country.BRAZIL,
                identity_document="123.456.789-09",
                requested_amount=2000.0,  # 40% of 5000
                monthly_income=5000.0
            )
        
        error_details = exc_info.value.rule_details
        assert error_details["country"] == "Brazil"
        assert "errors" in error_details
        assert len(error_details["errors"]) > 0
        assert error_details["errors"][0]["rule_type"] == "amount_to_income_ratio"
        assert error_details["errors"][0]["max_percentage"] == 30.0
        assert error_details["errors"][0]["requested_percentage"] == 40.0


@pytest.mark.asyncio
async def test_validate_country_rules_zero_income(mock_country_rule):
    """Test validation failure when monthly income is zero"""
    with patch('app.services.credit_request_service.get_country_rule_by_country', new_callable=AsyncMock) as mock_get_rule:
        mock_get_rule.return_value = mock_country_rule
        
        with pytest.raises(ValidationError) as exc_info:
            await validate_country_rules(
                country=Country.BRAZIL,
                identity_document="123.456.789-09",
                requested_amount=1000.0,
                monthly_income=0.0
            )
        
        error_details = exc_info.value.rule_details
        assert "errors" in error_details
        assert len(error_details["errors"]) > 0
        assert "mayor a cero" in error_details["errors"][0]["error_message"]

