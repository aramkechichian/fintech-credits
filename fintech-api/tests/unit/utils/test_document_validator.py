"""
Unit tests for document validator
"""
import pytest
from app.utils.document_validator import (
    validate_dni_spain,
    validate_nif_portugal,
    validate_cpf_brazil,
    validate_curp_mexico,
    validate_codice_fiscale_italy,
    validate_cedula_colombia,
    validate_document_format
)
from app.models.credit_request import Country


class TestValidateDNISpain:
    """Tests for Spanish DNI validation"""
    
    def test_valid_dni(self):
        """Test valid DNI format"""
        # DNI 12345678 -> 12345678 % 23 = 25 -> Z
        is_valid, error = validate_dni_spain("12345678Z")
        assert is_valid is True
        assert error is None
    
    def test_valid_dni_with_dash(self):
        """Test valid DNI with dash (should be normalized)"""
        is_valid, error = validate_dni_spain("12345678-Z")
        assert is_valid is True
        assert error is None
    
    def test_valid_dni_with_spaces(self):
        """Test valid DNI with spaces (should be normalized)"""
        is_valid, error = validate_dni_spain("12 345 678 Z")
        assert is_valid is True
        assert error is None
    
    def test_invalid_dni_wrong_letter(self):
        """Test DNI with wrong letter"""
        is_valid, error = validate_dni_spain("12345678A")
        assert is_valid is False
        assert "no es válida" in error
    
    def test_invalid_dni_wrong_format(self):
        """Test DNI with wrong format"""
        is_valid, error = validate_dni_spain("1234567Z")
        assert is_valid is False
        assert "8 dígitos" in error
    
    def test_invalid_dni_too_short(self):
        """Test DNI that is too short"""
        is_valid, error = validate_dni_spain("1234567")
        assert is_valid is False


class TestValidateNIFPortugal:
    """Tests for Portuguese NIF validation"""
    
    def test_valid_nif(self):
        """Test valid NIF format"""
        # NIF 123456789 - check digit 9 is valid
        is_valid, error = validate_nif_portugal("123456789")
        assert is_valid is True
        assert error is None
    
    def test_valid_nif_with_dashes(self):
        """Test valid NIF with dashes (should be normalized)"""
        is_valid, error = validate_nif_portugal("123-456-789")
        assert is_valid is True
        assert error is None
    
    def test_invalid_nif_wrong_check_digit(self):
        """Test NIF with wrong check digit"""
        is_valid, error = validate_nif_portugal("123456788")
        assert is_valid is False
        assert "dígito verificador" in error
    
    def test_invalid_nif_wrong_length(self):
        """Test NIF with wrong length"""
        is_valid, error = validate_nif_portugal("12345678")
        assert is_valid is False
        assert "9 dígitos" in error


class TestValidateCPFBrazil:
    """Tests for Brazilian CPF validation"""
    
    def test_valid_cpf(self):
        """Test valid CPF format (provided by user)"""
        is_valid, error = validate_cpf_brazil("123.456.789-09")
        assert is_valid is True
        assert error is None
    
    def test_valid_cpf_no_formatting(self):
        """Test valid CPF without formatting"""
        is_valid, error = validate_cpf_brazil("12345678909")
        assert is_valid is True
        assert error is None
    
    def test_invalid_cpf_all_same_digits(self):
        """Test CPF with all same digits (invalid)"""
        is_valid, error = validate_cpf_brazil("111.111.111-11")
        assert is_valid is False
        assert "todos los dígitos iguales" in error
    
    def test_invalid_cpf_wrong_check_digit(self):
        """Test CPF with wrong check digits"""
        is_valid, error = validate_cpf_brazil("123.456.789-00")
        assert is_valid is False
        assert "dígito verificador" in error
    
    def test_invalid_cpf_wrong_length(self):
        """Test CPF with wrong length"""
        is_valid, error = validate_cpf_brazil("123456789")
        assert is_valid is False
        assert "11 dígitos" in error


class TestValidateCURPMexico:
    """Tests for Mexican CURP validation"""
    
    def test_valid_curp(self):
        """Test valid CURP format"""
        is_valid, error = validate_curp_mexico("ABCD123456HDFXYZ01")
        assert is_valid is True
        assert error is None
    
    def test_valid_curp_with_dashes(self):
        """Test valid CURP with dashes (should be normalized)"""
        is_valid, error = validate_curp_mexico("ABCD-123456-HDF-XYZ-01")
        assert is_valid is True
        assert error is None
    
    def test_invalid_curp_wrong_format(self):
        """Test CURP with wrong format"""
        is_valid, error = validate_curp_mexico("ABCD123456")
        assert is_valid is False
        assert "18 caracteres" in error
    
    def test_invalid_curp_wrong_length(self):
        """Test CURP with wrong length"""
        is_valid, error = validate_curp_mexico("ABCD123456HDFXYZ0")
        assert is_valid is False


class TestValidateCodiceFiscaleItaly:
    """Tests for Italian Codice Fiscale validation"""
    
    def test_valid_codice_fiscale(self):
        """Test valid Codice Fiscale format"""
        is_valid, error = validate_codice_fiscale_italy("RSSMRA80A01H501U")
        assert is_valid is True
        assert error is None
    
    def test_valid_codice_fiscale_with_spaces(self):
        """Test valid Codice Fiscale with spaces (should be normalized)"""
        is_valid, error = validate_codice_fiscale_italy("RSSM RA80 A01H 501U")
        assert is_valid is True
        assert error is None
    
    def test_invalid_codice_fiscale_wrong_length(self):
        """Test Codice Fiscale with wrong length"""
        is_valid, error = validate_codice_fiscale_italy("RSSMRA80A01H501")
        assert is_valid is False
        assert "16 caracteres" in error


class TestValidateCedulaColombia:
    """Tests for Colombian Cédula validation"""
    
    def test_valid_cedula_8_digits(self):
        """Test valid Cédula with 8 digits"""
        is_valid, error = validate_cedula_colombia("12345678")
        assert is_valid is True
        assert error is None
    
    def test_valid_cedula_10_digits(self):
        """Test valid Cédula with 10 digits"""
        is_valid, error = validate_cedula_colombia("1234567890")
        assert is_valid is True
        assert error is None
    
    def test_valid_cedula_with_dots(self):
        """Test valid Cédula with dots (should be normalized)"""
        is_valid, error = validate_cedula_colombia("12.345.678")
        assert is_valid is True
        assert error is None
    
    def test_invalid_cedula_too_short(self):
        """Test Cédula that is too short"""
        is_valid, error = validate_cedula_colombia("1234567")
        assert is_valid is False
        assert "8 y 10" in error or "entre 8 y 10" in error
    
    def test_invalid_cedula_too_long(self):
        """Test Cédula that is too long"""
        is_valid, error = validate_cedula_colombia("12345678901")
        assert is_valid is False


class TestValidateDocumentFormat:
    """Tests for the main document format validator"""
    
    def test_validate_dni_spain(self):
        """Test DNI validation for Spain"""
        is_valid, error = validate_document_format(
            Country.SPAIN,
            "DNI",
            "12345678Z"
        )
        assert is_valid is True
        assert error is None
    
    def test_validate_nif_portugal(self):
        """Test NIF validation for Portugal"""
        is_valid, error = validate_document_format(
            Country.PORTUGAL,
            "NIF",
            "123456789"
        )
        assert is_valid is True
        assert error is None
    
    def test_validate_cpf_brazil(self):
        """Test CPF validation for Brazil"""
        is_valid, error = validate_document_format(
            Country.BRAZIL,
            "CPF",
            "123.456.789-09"
        )
        assert is_valid is True
        assert error is None
    
    def test_validate_curp_mexico(self):
        """Test CURP validation for Mexico"""
        is_valid, error = validate_document_format(
            Country.MEXICO,
            "CURP",
            "ABCD123456HDFXYZ01"
        )
        assert is_valid is True
        assert error is None
    
    def test_validate_codice_fiscale_italy(self):
        """Test Codice Fiscale validation for Italy"""
        is_valid, error = validate_document_format(
            Country.ITALY,
            "Codice Fiscale",
            "RSSMRA80A01H501U"
        )
        assert is_valid is True
        assert error is None
    
    def test_validate_cedula_colombia(self):
        """Test Cédula validation for Colombia"""
        is_valid, error = validate_document_format(
            Country.COLOMBIA,
            "Cédula de Ciudadanía",
            "12345678"
        )
        assert is_valid is True
        assert error is None
    
    def test_validate_empty_document(self):
        """Test validation with empty document"""
        is_valid, error = validate_document_format(
            Country.SPAIN,
            "DNI",
            ""
        )
        assert is_valid is False
        assert "requerido" in error
    
    def test_validate_unknown_country_document(self):
        """Test validation with unknown country/document combination"""
        # Should do basic validation (length check)
        is_valid, error = validate_document_format(
            Country.SPAIN,
            "Unknown",
            "AB"
        )
        assert is_valid is False
        assert "al menos 3 caracteres" in error
    
    def test_validate_document_too_long(self):
        """Test validation with document that is too long"""
        is_valid, error = validate_document_format(
            Country.SPAIN,
            "Unknown",
            "A" * 51  # More than 50 characters
        )
        assert is_valid is False
        assert "más de 50 caracteres" in error
