from datetime import datetime
from typing import Optional
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

logger = logging.getLogger(__name__)

async def create_credit_request(
    user_id: str,
    credit_request_data: CreditRequestCreate,
    bank_information: Optional[BankInformation] = None
) -> CreditRequestInDB:
    """
    Create a new credit request
    
    This function triggers additional logic:
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
