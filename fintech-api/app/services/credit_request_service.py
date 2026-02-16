from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
import logging
from app.models.credit_request import (
    CreditRequestCreate,
    CreditRequestInDB,
    CreditRequestStatus,
    BankInformation,
    CurrencyCode,
    Country,
    COUNTRY_CURRENCY_MAP
)
from app.repositories.credit_request_repository import credit_request_repository
from app.services.log_service import log_request
from app.services.country_rule_service import get_country_rule_by_country
from app.models.country_rule import ValidationRule
from app.utils.document_validator import validate_document_format
from app.utils.valid_documents_examples import ONE_EXAMPLE_PER_COUNTRY_CLEAN

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors with rule details"""
    def __init__(self, message: str, rule_details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.rule_details = rule_details or {}
        super().__init__(self.message)


async def validate_country_rules(
    country: Country,
    identity_document: str,
    requested_amount: float,
    monthly_income: float
) -> None:
    """
    Validate credit request against country rules
    
    Raises:
        ValidationError: If validation fails, includes rule details
    """
    # Get country rule
    country_rule = await get_country_rule_by_country(country)
    
    if not country_rule:
        logger.warning(f"No country rule found for {country}, skipping validation")
        return
    
    if not country_rule.is_active:
        logger.info(f"Country rule for {country} is inactive, skipping validation")
        return
    
    # Validate document format first
    validation_errors: List[Dict[str, Any]] = []
    
    # Validate document format
    is_valid_doc, doc_error = validate_document_format(
        country=country,
        document_type=country_rule.required_document_type,
        document=identity_document
    )
    
    if not is_valid_doc:
        # Get example for the country
        country_name = country.value
        example = ONE_EXAMPLE_PER_COUNTRY_CLEAN.get(country_name, "")
        example_text = f". Ejemplo válido: {example}" if example else ""
        
        error_detail = {
            "rule_type": "document_format",
            "required_document_type": country_rule.required_document_type,
            "provided_document": identity_document,
            "error_message": doc_error or f"El formato del documento {country_rule.required_document_type} no es válido para {country.value}{example_text}"
        }
        validation_errors.append(error_detail)
    
    for rule in country_rule.validation_rules:
        if not rule.enabled:
            continue
        
        # Validate amount vs income ratio
        if monthly_income > 0:
            percentage = (requested_amount / monthly_income) * 100
            
            if percentage > rule.max_percentage:
                error_detail = {
                    "rule_type": "amount_to_income_ratio",
                    "max_percentage": rule.max_percentage,
                    "requested_percentage": round(percentage, 2),
                    "requested_amount": requested_amount,
                    "monthly_income": monthly_income,
                    "error_message": rule.error_message or f"El monto solicitado ({requested_amount}) excede el {rule.max_percentage}% del ingreso mensual ({monthly_income}). Porcentaje calculado: {round(percentage, 2)}%"
                }
                validation_errors.append(error_detail)
        else:
            # If monthly income is 0 or negative, this is invalid
            error_detail = {
                "rule_type": "amount_to_income_ratio",
                "max_percentage": rule.max_percentage,
                "requested_percentage": None,
                "requested_amount": requested_amount,
                "monthly_income": monthly_income,
                "error_message": "El ingreso mensual debe ser mayor a cero"
            }
            validation_errors.append(error_detail)
    
    # If there are validation errors, raise exception with details
    if validation_errors:
        error_messages = [err["error_message"] for err in validation_errors]
        main_message = "La solicitud no cumple con las reglas de validación del país"
        
        raise ValidationError(
            message=main_message,
            rule_details={
                "country": country.value,
                "required_document_type": country_rule.required_document_type,
                "errors": validation_errors,
                "summary": "; ".join(error_messages)
            }
        )

async def create_credit_request(
    user_id: str,
    credit_request_data: CreditRequestCreate,
    bank_information: Optional[BankInformation] = None
) -> CreditRequestInDB:
    """
    Create a new credit request
    
    This function triggers additional logic:
    - Country rules validation
    - Risk validation
    - Audit logging
    - Background processing
    
    TODO: Implement the following additional logic:
    1. Risk validation based on requested_amount, monthly_income, and country
    2. Audit logging for compliance
    3. Background processing (e.g., credit score check, fraud detection)
    4. Notification system (email/SMS to user)
    5. Integration with external credit bureaus
    """
    logger.info(f"Creating credit request for user {user_id}")
    
    # Get currency code based on country
    # The country comes as a string from the API, so we need to convert it to the enum
    country_enum = credit_request_data.country
    if isinstance(country_enum, str):
        # Convert string to Country enum
        try:
            country_enum = Country(country_enum)
        except ValueError:
            logger.error(f"Invalid country value: {country_enum}")
            raise ValueError(f"Invalid country: {country_enum}")
    
        # Validate against country rules BEFORE creating the request
    try:
        await validate_country_rules(
            country=country_enum,
            identity_document=credit_request_data.identity_document,
            requested_amount=credit_request_data.requested_amount,
            monthly_income=credit_request_data.monthly_income
        )
    except ValidationError as e:
        logger.warning(f"Credit request validation failed for user {user_id}: {e.message}")
        # Re-raise the validation error with details
        raise
    
    # Get currency code from map
    currency_code = COUNTRY_CURRENCY_MAP.get(country_enum)
    if not currency_code:
        logger.warning(f"Country {country_enum} not found in currency map, using EUR as fallback")
        currency_code = CurrencyCode.EUR
    
    # Create credit request object
    credit_request = CreditRequestInDB(
        user_id=ObjectId(user_id),
        country=credit_request_data.country,
        currency_code=currency_code,
        full_name=credit_request_data.full_name,
        identity_document=credit_request_data.identity_document,
        requested_amount=credit_request_data.requested_amount,
        monthly_income=credit_request_data.monthly_income,
        request_date=datetime.utcnow(),
        status=CreditRequestStatus.PENDING,
        bank_information=bank_information,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save to database
    created_request = await credit_request_repository.create(credit_request)
    
    logger.info(f"Credit request {created_request.id} created successfully")
    
    # Log the request creation (this is called from service, controller will also log the full request/response)
    try:
        await log_request(
            endpoint="/credit-requests",
            method="POST",
            user_id=user_id,
            payload={
                "country": credit_request_data.country.value if hasattr(credit_request_data.country, 'value') else str(credit_request_data.country),
                "full_name": credit_request_data.full_name,
                "identity_document": credit_request_data.identity_document,
                "requested_amount": credit_request_data.requested_amount,
                "monthly_income": credit_request_data.monthly_income,
                "currency_code": currency_code.value
            },
            response_status=201,
            is_success=True
        )
    except Exception as e:
        logger.error(f"Error logging credit request creation: {str(e)}", exc_info=True)
    
    # TODO: Additional logic to be implemented:
    # 
    # 1. Risk Validation
    # - Calculate debt-to-income ratio
    # - Check if requested amount is reasonable based on monthly income
    # - Validate country-specific requirements
    # - Check user's credit history (if available)
    #
    # 2. Audit Logging
    # - Log the creation event with all relevant details
    # - Store audit trail for compliance purposes
    # - Track changes to the request status
    #
    # 3. Background Processing
    # - Send request to credit bureau for verification
    # - Run fraud detection algorithms
    # - Check against blacklists or watchlists
    # - Calculate credit score
    #
    # 4. Notification System
    # - Send confirmation email to user
    # - Notify internal team of new request
    # - Set up status update notifications
    #
    # 5. External Integrations
    # - Integrate with credit bureaus (Equifax, TransUnion, etc.)
    # - Connect with banking APIs for verification
    # - Integrate with KYC/AML services
    
    return created_request

async def get_credit_request_by_id(request_id: str) -> Optional[CreditRequestInDB]:
    """Get a credit request by ID"""
    return await credit_request_repository.get_by_id(request_id)

async def get_user_credit_requests(user_id: str) -> list[CreditRequestInDB]:
    """Get all credit requests for a user"""
    return await credit_request_repository.get_by_user_id(user_id)

async def update_credit_request_status(
    request_id: str,
    new_status: CreditRequestStatus,
    bank_information: Optional[BankInformation] = None
) -> Optional[CreditRequestInDB]:
    """Update credit request status"""
    update_data = {"status": new_status}
    if bank_information:
        update_data["bank_information"] = bank_information.model_dump()
    
    updated_request = await credit_request_repository.update(request_id, update_data)
    
    # TODO: Send email notification to user when status changes to approved or rejected
    # if updated_request and new_status in [CreditRequestStatus.APPROVED, CreditRequestStatus.REJECTED]:
    #     # Get user email from user_id
    #     from app.repositories.user_repository import user_repository
    #     user = await user_repository.get_by_id(str(updated_request.user_id))
    #     if user:
    #         await send_email(
    #             to=user.email,
    #             subject=f"Credit Request {new_status.value}",
    #             body=f"Your credit request has been {new_status.value}."
    #         )
    
    return updated_request

async def search_credit_requests(
    user_id: str,
    countries: Optional[list[str]] = None,
    identity_document: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> tuple[list[CreditRequestInDB], int]:
    """
    Search credit requests with filters and pagination
    
    Returns:
        tuple: (list of requests, total count)
    """
    return await credit_request_repository.search(
        user_id=user_id,
        countries=countries,
        identity_document=identity_document,
        status=status,
        skip=skip,
        limit=limit
    )
