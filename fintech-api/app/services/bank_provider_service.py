"""
Service for bank provider integration
Handles communication with different bank providers per country
"""
import logging
from typing import Optional, Dict, Any
from app.models.credit_request import Country
from app.models.credit_request import BankInformation

logger = logging.getLogger(__name__)


async def get_bank_information(
    country: Country,
    full_name: str,
    identity_document: str
) -> Dict[str, Any]:
    """
    Get bank information from provider for a given country
    
    Args:
        country: Country enum
        full_name: Full name of the person
        identity_document: Identity document number
        
    Returns:
        Dict with bank information or error message
        
    Note:
        Currently returns a placeholder message. This function is prepared
        for future integration with actual bank provider APIs.
    """
    logger.info(f"Requesting bank information for country: {country}, document: {identity_document}")
    
    # TODO: Implement actual bank provider integration
    # This will be implemented based on the specific provider for each country:
    # - Brazil: Integrate with Brazilian bank provider API
    # - Spain: Integrate with Spanish bank provider API
    # - Mexico: Integrate with Mexican bank provider API
    # - Colombia: Integrate with Colombian bank provider API
    # - Italy: Integrate with Italian bank provider API
    # - Portugal: Integrate with Portuguese bank provider API
    
    # For now, return a placeholder response
    # This challenge leaves prepared the possibility to connect all required APIs
    country_name = country.value if hasattr(country, 'value') else str(country)
    
    return {
        "status": "not_connected",
        "message": f"No existe ninguna API externa conectada para el país {country_name}.",
        "description": "Este challenge deja preparada la posibilidad de conectar todas las APIs que se requieran. La arquitectura está lista para integrar proveedores bancarios específicos por país cuando sea necesario.",
        "country": country_name,
        "full_name": full_name,
        "identity_document": identity_document,
        "bank_information": None
    }


async def fetch_bank_information_from_provider(
    country: Country,
    identity_document: str,
    full_name: Optional[str] = None
) -> Optional[BankInformation]:
    """
    Fetch bank information from provider and convert to BankInformation model
    
    Args:
        country: Country enum
        identity_document: Identity document number
        full_name: Optional full name for verification
        
    Returns:
        BankInformation object if successful, None otherwise
        
    Note:
        This function will be implemented when bank provider APIs are integrated.
        It will call the appropriate provider based on country and normalize
        the response to BankInformation model.
    """
    logger.info(f"Fetching bank information from provider for {country}, document: {identity_document}")
    
    # Get bank information from provider
    provider_response = await get_bank_information(
        country=country,
        full_name=full_name or "",
        identity_document=identity_document
    )
    
    # If provider is not connected, return None
    if provider_response.get("status") == "not_connected":
        logger.warning(f"Bank provider not connected for country: {country}")
        return None
    
    # TODO: When provider is connected, parse the response and create BankInformation
    # Example:
    # if provider_response.get("status") == "success":
    #     return BankInformation(
    #         bank_name=provider_response.get("bank_name"),
    #         account_number=provider_response.get("account_number"),
    #         account_type=provider_response.get("account_type"),
    #         routing_number=provider_response.get("routing_number"),
    #         iban=provider_response.get("iban"),
    #         swift=provider_response.get("swift"),
    #         provider_data=provider_response.get("raw_data")
    #     )
    
    return None
