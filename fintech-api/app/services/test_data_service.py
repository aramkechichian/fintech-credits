"""
Test data service for generating and cleaning test data
"""
import logging
from typing import List
from datetime import datetime, timedelta
from random import choice, uniform, randint
from bson import ObjectId

from app.models.credit_request import (
    CreditRequestInDB,
    CreditRequestStatus,
    Country,
    CurrencyCode,
    COUNTRY_CURRENCY_MAP
)
from app.repositories.credit_request_repository import CreditRequestRepository
from app.utils.valid_documents_examples import (
    ONE_EXAMPLE_PER_COUNTRY_CLEAN
)

logger = logging.getLogger(__name__)

# Repository instance
credit_request_repository = CreditRequestRepository()

# Email domains for test data
TEST_EMAIL_DOMAINS = ["test.com", "example.com", "demo.com", "sample.org"]

# Name pools for random generation
FIRST_NAMES = [
    "Juan", "María", "Carlos", "Ana", "Luis", "Laura", "Pedro", "Carmen",
    "José", "Isabel", "Miguel", "Patricia", "Francisco", "Lucía", "Antonio",
    "Sofía", "Manuel", "Elena", "David", "Marta", "Javier", "Paula",
    "Roberto", "Andrea", "Fernando", "Natalia", "Ricardo", "Claudia"
]

LAST_NAMES = [
    "García", "Rodríguez", "González", "Fernández", "López", "Martínez",
    "Sánchez", "Pérez", "Gómez", "Martín", "Jiménez", "Ruiz", "Hernández",
    "Díaz", "Moreno", "Muñoz", "Álvarez", "Romero", "Alonso", "Gutiérrez",
    "Navarro", "Torres", "Domínguez", "Vázquez", "Ramos", "Gil", "Ramírez"
]


def _get_random_name() -> str:
    """Generate a random full name"""
    first_name = choice(FIRST_NAMES)
    last_name = choice(LAST_NAMES)
    return f"{first_name} {last_name}"


def _get_random_email(full_name: str) -> str:
    """Generate a random email based on name"""
    name_part = full_name.lower().replace(" ", ".")
    domain = choice(TEST_EMAIL_DOMAINS)
    number = randint(1, 9999)
    return f"{name_part}{number}@{domain}"


def _get_random_date_in_range(days_back: int = 90) -> datetime:
    """Generate a random date within the last N days"""
    days_ago = randint(0, days_back)
    return datetime.utcnow() - timedelta(days=days_ago)


def _get_country_currency(country: Country) -> CurrencyCode:
    """Get the currency code for a country"""
    # Use the mapping from the model
    return COUNTRY_CURRENCY_MAP.get(country, CurrencyCode.EUR)


async def generate_random_credit_requests(count: int = 50) -> List[CreditRequestInDB]:
    """
    Generate random credit requests for testing
    
    Args:
        count: Number of requests to generate
        
    Returns:
        List of created CreditRequestInDB objects
    """
    logger.info(f"Generating {count} random credit requests for testing")
    
    created_requests = []
    countries = list(Country)
    statuses = list(CreditRequestStatus)
    
    for i in range(count):
        try:
            # Random country
            country = choice(countries)
            
            # Get valid document for country
            identity_document = ONE_EXAMPLE_PER_COUNTRY_CLEAN.get(country.value, "123456789")
            
            # Random name and email
            full_name = _get_random_name()
            email = _get_random_email(full_name)
            
            # Random amounts (realistic ranges)
            monthly_income = round(uniform(1000.0, 10000.0), 2)
            # Requested amount between 20% and 80% of monthly income (to have variety)
            percentage = uniform(0.2, 0.8)
            requested_amount = round(monthly_income * percentage, 2)
            
            # Random status (weighted towards pending)
            status_weights = {
                CreditRequestStatus.PENDING: 0.4,
                CreditRequestStatus.IN_REVIEW: 0.2,
                CreditRequestStatus.APPROVED: 0.2,
                CreditRequestStatus.REJECTED: 0.2,
            }
            status = choice(list(status_weights.keys()))
            
            # Random date within last 90 days
            request_date = _get_random_date_in_range(90)
            
            # Get currency code for country
            currency_code = _get_country_currency(country)
            
            # Create in database directly
            credit_request = CreditRequestInDB(
                id=ObjectId(),
                country=country,
                currency_code=currency_code,
                full_name=full_name,
                email=email,
                identity_document=identity_document,
                requested_amount=requested_amount,
                monthly_income=monthly_income,
                request_date=request_date,
                status=status,
                bank_information=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save to database
            created_request = await credit_request_repository.create(credit_request)
            created_requests.append(created_request)
            
        except Exception as e:
            logger.error(f"Error generating credit request {i+1}: {str(e)}", exc_info=True)
            continue
    
    logger.info(f"Successfully generated {len(created_requests)} credit requests")
    return created_requests


async def clear_all_credit_requests() -> int:
    """
    Delete all credit requests from the database
    
    Returns:
        Number of deleted requests
    """
    logger.info("Clearing all credit requests from database")
    
    try:
        from app.core.database import get_database
        
        db = get_database()
        collection = db["credit_requests"]
        
        # Delete all documents
        result = await collection.delete_many({})
        deleted_count = result.deleted_count
        
        logger.info(f"Successfully deleted {deleted_count} credit requests")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error clearing credit requests: {str(e)}", exc_info=True)
        raise
