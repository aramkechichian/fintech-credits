"""
Initialize default country rules on application startup
"""
import logging
from app.models.country_rule import CountryRuleCreate, ValidationRule
from app.models.credit_request import Country
from app.services.country_rule_service import (
    get_country_rule_by_country,
    create_country_rule
)

logger = logging.getLogger(__name__)


async def initialize_default_country_rules():
    """Initialize default country rules if they don't exist"""
    logger.info("Initializing default country rules...")
    
    default_rules = [
        {
            "country": Country.SPAIN,
            "required_document_type": "DNI",
            "description": "Reglas de validación para España - DNI requerido",
            "validation_rules": [
                ValidationRule(
                    max_percentage=30.0,
                    enabled=True,
                    error_message="El monto solicitado no puede exceder el 30% del ingreso mensual"
                )
            ]
        },
        {
            "country": Country.PORTUGAL,
            "required_document_type": "NIF",
            "description": "Reglas de validación para Portugal - NIF requerido",
            "validation_rules": [
                ValidationRule(
                    max_percentage=30.0,
                    enabled=True,
                    error_message="El monto solicitado no puede exceder el 30% del ingreso mensual"
                )
            ]
        },
        {
            "country": Country.ITALY,
            "required_document_type": "Codice Fiscale",
            "description": "Reglas de validación para Italia - Codice Fiscale requerido",
            "validation_rules": [
                ValidationRule(
                    max_percentage=35.0,
                    enabled=True,
                    error_message="El monto solicitado no puede exceder el 35% del ingreso mensual"
                )
            ]
        },
        {
            "country": Country.MEXICO,
            "required_document_type": "CURP",
            "description": "Reglas de validación para México - CURP requerido",
            "validation_rules": [
                ValidationRule(
                    max_percentage=40.0,
                    enabled=True,
                    error_message="El monto solicitado no puede exceder el 40% del ingreso mensual"
                )
            ]
        },
        {
            "country": Country.COLOMBIA,
            "required_document_type": "Cédula de Ciudadanía",
            "description": "Reglas de validación para Colombia - Cédula de Ciudadanía requerida",
            "validation_rules": [
                ValidationRule(
                    max_percentage=50.0,
                    enabled=True,
                    error_message="El monto solicitado no puede exceder el 50% del ingreso mensual"
                )
            ]
        },
        {
            "country": Country.BRAZIL,
            "required_document_type": "CPF",
            "description": "Reglas de validación para Brasil - CPF requerido",
            "validation_rules": [
                ValidationRule(
                    max_percentage=35.0,
                    enabled=True,
                    error_message="O valor solicitado não pode exceder 35% da renda mensal"
                )
            ]
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for rule_data in default_rules:
        try:
            # Check if rule already exists
            existing_rule = await get_country_rule_by_country(rule_data["country"])
            
            if existing_rule:
                logger.info(f"Country rule for {rule_data['country']} already exists, skipping...")
                skipped_count += 1
                continue
            
            # Create the rule
            country_rule = CountryRuleCreate(**rule_data)
            await create_country_rule(country_rule_data=country_rule, created_by=None)
            created_count += 1
            logger.info(f"Created default country rule for {rule_data['country']}")
            
        except Exception as e:
            logger.error(f"Error creating default country rule for {rule_data['country']}: {str(e)}", exc_info=True)
    
    logger.info(f"Country rules initialization completed. Created: {created_count}, Skipped: {skipped_count}")
