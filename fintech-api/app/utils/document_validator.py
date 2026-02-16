"""
Document format validator for different countries
"""
import re
from typing import Optional, Tuple
from app.models.credit_request import Country
from app.models.country_rule import DocumentType

logger = None  # Will be initialized if needed


def validate_dni_spain(document: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Spanish DNI format
    Format: 8 digits + 1 letter (e.g., 12345678Z)
    """
    # Remove spaces and convert to uppercase
    document = document.replace(" ", "").replace("-", "").upper()
    
    # Pattern: 8 digits followed by 1 letter
    pattern = r'^[0-9]{8}[A-Z]$'
    
    if not re.match(pattern, document):
        return False, "El DNI debe tener 8 dígitos seguidos de una letra (ej: 12345678Z)"
    
    # Validate letter (DNI letter validation)
    digits = document[:8]
    letter = document[8]
    
    # DNI letter calculation
    letter_index = int(digits) % 23
    valid_letters = "TRWAGMYFPDXBNJZSQVHLCKE"
    expected_letter = valid_letters[letter_index]
    
    if letter != expected_letter:
        return False, f"La letra del DNI no es válida. Debería ser {expected_letter}"
    
    return True, None


def validate_nif_portugal(document: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Portuguese NIF format
    Format: 9 digits (last digit is check digit)
    """
    # Remove spaces and dashes
    document = document.replace(" ", "").replace("-", "")
    
    # Pattern: 9 digits
    pattern = r'^[0-9]{9}$'
    
    if not re.match(pattern, document):
        return False, "El NIF debe tener 9 dígitos"
    
    # Validate check digit
    if len(document) == 9:
        digits = [int(d) for d in document[:8]]
        check_digit = int(document[8])
        
        # NIF validation algorithm
        weights = [9, 8, 7, 6, 5, 4, 3, 2]
        total = sum(d * w for d, w in zip(digits, weights))
        remainder = total % 11
        
        if remainder < 2:
            expected_check = 0
        else:
            expected_check = 11 - remainder
        
        if check_digit != expected_check:
            return False, "El dígito verificador del NIF no es válido"
    
    return True, None


def validate_cpf_brazil(document: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Brazilian CPF format
    Format: 11 digits (with check digits)
    """
    # Remove spaces, dots, and dashes
    document = re.sub(r'[.\-\s]', '', document)
    
    # Pattern: 11 digits
    pattern = r'^[0-9]{11}$'
    
    if not re.match(pattern, document):
        return False, "El CPF debe tener 11 dígitos"
    
    # Check for known invalid CPFs (all same digits)
    if len(set(document)) == 1:
        return False, "El CPF no puede tener todos los dígitos iguales"
    
    # Validate check digits
    digits = [int(d) for d in document[:9]]
    
    # First check digit
    weights1 = list(range(10, 1, -1))
    total1 = sum(d * w for d, w in zip(digits, weights1))
    remainder1 = total1 % 11
    check1 = 0 if remainder1 < 2 else 11 - remainder1
    
    if check1 != int(document[9]):
        return False, "El primer dígito verificador del CPF no es válido"
    
    # Second check digit
    digits.append(check1)
    weights2 = list(range(11, 1, -1))
    total2 = sum(d * w for d, w in zip(digits, weights2))
    remainder2 = total2 % 11
    check2 = 0 if remainder2 < 2 else 11 - remainder2
    
    if check2 != int(document[10]):
        return False, "El segundo dígito verificador del CPF no es válido"
    
    return True, None


def validate_curp_mexico(document: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Mexican CURP format
    Format: 18 alphanumeric characters
    Structure: 4 letters + 6 digits (date) + 1 letter (sex) + 2 letters (state) + 3 letters + 1 letter + 1 digit
    """
    # Remove spaces and convert to uppercase
    document = document.replace(" ", "").replace("-", "").upper()
    
    # Pattern: 18 alphanumeric characters
    pattern = r'^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[0-9A-Z][0-9]$'
    
    if not re.match(pattern, document):
        return False, "El CURP debe tener 18 caracteres alfanuméricos en el formato correcto"
    
    return True, None


def validate_codice_fiscale_italy(document: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Italian Codice Fiscale format
    Format: 16 alphanumeric characters
    """
    # Remove spaces and convert to uppercase
    document = document.replace(" ", "").replace("-", "").upper()
    
    # Pattern: 16 alphanumeric characters
    pattern = r'^[A-Z0-9]{16}$'
    
    if not re.match(pattern, document):
        return False, "El Codice Fiscale debe tener 16 caracteres alfanuméricos"
    
    # Basic structure validation (not full algorithm, but format check)
    # Codice Fiscale has a specific structure but we'll do basic format validation
    return True, None


def validate_cedula_colombia(document: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Colombian Cédula de Ciudadanía format
    Format: 8-10 digits
    """
    # Remove spaces and dashes
    document = document.replace(" ", "").replace("-", "").replace(".", "")
    
    # Pattern: 8-10 digits
    pattern = r'^[0-9]{8,10}$'
    
    if not re.match(pattern, document):
        return False, "La Cédula de Ciudadanía debe tener entre 8 y 10 dígitos"
    
    return True, None


def validate_document_format(
    country: Country,
    document_type: str,
    document: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate document format based on country and document type
    
    Args:
        country: Country enum
        document_type: Type of document (DNI, NIF, CPF, etc.)
        document: Document number to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not document or not document.strip():
        return False, "El documento de identidad es requerido"
    
    # Normalize document type
    document_type_upper = document_type.upper().strip()
    document_clean = document.strip()
    
    # Map country and document type to validator
    validators = {
        (Country.SPAIN, "DNI"): validate_dni_spain,
        (Country.PORTUGAL, "NIF"): validate_nif_portugal,
        (Country.BRAZIL, "CPF"): validate_cpf_brazil,
        (Country.MEXICO, "CURP"): validate_curp_mexico,
        (Country.ITALY, "CODICE FISCALE"): validate_codice_fiscale_italy,
        (Country.COLOMBIA, "CÉDULA DE CIUDADANÍA"): validate_cedula_colombia,
        (Country.COLOMBIA, "CEDULA DE CIUDADANIA"): validate_cedula_colombia,
        (Country.COLOMBIA, "CC"): validate_cedula_colombia,
    }
    
    # Try exact match first
    key = (country, document_type_upper)
    if key in validators:
        return validators[key](document_clean)
    
    # Try case-insensitive partial match
    for (c, dt), validator in validators.items():
        if c == country and dt in document_type_upper or document_type_upper in dt:
            return validator(document_clean)
    
    # If no specific validator found, do basic validation
    # At least check it's not empty and has reasonable length
    if len(document_clean) < 3:
        return False, f"El documento {document_type} debe tener al menos 3 caracteres"
    
    if len(document_clean) > 50:
        return False, f"El documento {document_type} no puede tener más de 50 caracteres"
    
    # For unknown formats, just check basic structure
    return True, None
