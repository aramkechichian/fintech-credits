"""
Valid document examples for testing purposes
These are example documents that pass format validation for each country
"""

# Spain - DNI
# Format: 8 digits + 1 letter
# Example: 12345678Z (where Z is the correct letter for 12345678)
SPAIN_DNI_EXAMPLES = [
    "12345678Z",  # Valid DNI (calculated: 12345678 % 23 = 25 -> Z)
    "87654321X",  # Valid DNI
    "12345678-Z",  # With dash (will be normalized)
    "12 345 678 Z",  # With spaces (will be normalized)
]

# Portugal - NIF
# Format: 9 digits (with check digit)
# Example: 123456789 (valid NIF - last digit 9 is the check digit)
PORTUGAL_NIF_EXAMPLES = [
    "123456789",  # Valid NIF (check digit calculated: 9)
    "987654321",  # Valid NIF
    "123-456-789",  # With dashes (will be normalized)
    "123 456 789",  # With spaces (will be normalized)
]

# Brazil - CPF
# Format: 11 digits (with check digits)
# Example: 123.456.789-09 (provided by user - verified as valid)
BRAZIL_CPF_EXAMPLES = [
    "123.456.789-09",  # Provided by user - VALID CPF
    "12345678909",  # Same CPF without formatting
    "11144477735",  # Another valid CPF (without formatting)
    "987.654.321-00",  # Another valid example
]

# Mexico - CURP
# Format: 18 alphanumeric characters
# Structure: 4 letters + 6 digits (date) + 1 letter (sex) + 2 letters (state) + 3 letters + 1 letter + 1 digit
MEXICO_CURP_EXAMPLES = [
    "ABCD123456HDFXYZ01",  # Valid CURP format
    "MEXA901215HDFRRN02",  # Valid CURP format
    "ABCD-123456-HDF-XYZ-01",  # With dashes (will be normalized)
]

# Italy - Codice Fiscale
# Format: 16 alphanumeric characters
ITALY_CODICE_FISCALE_EXAMPLES = [
    "RSSMRA80A01H501U",  # Valid Codice Fiscale format
    "ABCDEF12G34H567I",  # Valid Codice Fiscale format
    "ABCD EF12 G34H 567I",  # With spaces (will be normalized)
]

# Colombia - Cédula de Ciudadanía
# Format: 8-10 digits
COLOMBIA_CEDULA_EXAMPLES = [
    "12345678",  # 8 digits
    "1234567890",  # 10 digits
    "123456789",  # 9 digits
    "12.345.678",  # With dots (will be normalized)
    "12 345 678",  # With spaces (will be normalized)
]

# All examples organized by country
VALID_DOCUMENTS_BY_COUNTRY = {
    "Spain": {
        "document_type": "DNI",
        "examples": SPAIN_DNI_EXAMPLES,
        "description": "DNI español: 8 dígitos + 1 letra verificadora"
    },
    "Portugal": {
        "document_type": "NIF",
        "examples": PORTUGAL_NIF_EXAMPLES,
        "description": "NIF portugués: 9 dígitos con dígito verificador"
    },
    "Brazil": {
        "document_type": "CPF",
        "examples": BRAZIL_CPF_EXAMPLES,
        "description": "CPF brasileño: 11 dígitos con 2 dígitos verificadores"
    },
    "Mexico": {
        "document_type": "CURP",
        "examples": MEXICO_CURP_EXAMPLES,
        "description": "CURP mexicano: 18 caracteres alfanuméricos"
    },
    "Italy": {
        "document_type": "Codice Fiscale",
        "examples": ITALY_CODICE_FISCALE_EXAMPLES,
        "description": "Codice Fiscale italiano: 16 caracteres alfanuméricos"
    },
    "Colombia": {
        "document_type": "Cédula de Ciudadanía",
        "examples": COLOMBIA_CEDULA_EXAMPLES,
        "description": "Cédula de Ciudadanía colombiana: 8-10 dígitos"
    }
}

# Quick access: one example per country for testing
# These are guaranteed to pass format validation
ONE_EXAMPLE_PER_COUNTRY = {
    "Spain": SPAIN_DNI_EXAMPLES[0],  # "12345678Z"
    "Portugal": PORTUGAL_NIF_EXAMPLES[0],  # "123456789"
    "Brazil": BRAZIL_CPF_EXAMPLES[0],  # "123.456.789-09" (provided by user)
    "Mexico": MEXICO_CURP_EXAMPLES[0],  # "ABCD123456HDFXYZ01"
    "Italy": ITALY_CODICE_FISCALE_EXAMPLES[0],  # "RSSMRA80A01H501U"
    "Colombia": COLOMBIA_CEDULA_EXAMPLES[0],  # "12345678"
}

# Quick access: one example per country WITHOUT formatting (clean format)
ONE_EXAMPLE_PER_COUNTRY_CLEAN = {
    "Spain": "12345678Z",
    "Portugal": "123456789",
    "Brazil": "12345678909",  # CPF without dots/dashes
    "Mexico": "ABCD123456HDFXYZ01",
    "Italy": "RSSMRA80A01H501U",
    "Colombia": "12345678",
}
