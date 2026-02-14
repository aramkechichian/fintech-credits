"""
Country Rule models for validation rules per country
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from bson import ObjectId
from app.models.credit_request import Country

class DocumentType(str, Enum):
    """Document types per country"""
    DNI = "DNI"  # Spain
    NIF = "NIF"  # Portugal
    CODICE_FISCALE = "Codice Fiscale"  # Italy
    CURP = "CURP"  # Mexico
    CC = "Cédula de Ciudadanía"  # Colombia
    CPF = "CPF"  # Brazil


class ValidationRule(BaseModel):
    """Validation rule for amount to income ratio"""
    max_percentage: float = Field(..., description="Maximum percentage of monthly income that can be requested (e.g., 30.0 for 30%)")
    enabled: bool = Field(default=True, description="Whether this rule is active")
    error_message: Optional[str] = Field(None, description="Custom error message when rule fails")


class CountryRuleBase(BaseModel):
    """Base country rule schema"""
    country: Country = Field(..., description="Country code")
    required_document_type: str = Field(..., description="Required document type for this country")
    description: Optional[str] = Field(None, description="Description of the country rules")
    is_active: bool = Field(default=True, description="Whether these rules are active")


class CountryRuleCreate(CountryRuleBase):
    """Schema for creating a country rule"""
    validation_rules: List[ValidationRule] = Field(default_factory=list, description="List of validation rules")


class CountryRuleUpdate(BaseModel):
    """Schema for updating a country rule"""
    required_document_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    validation_rules: Optional[List[ValidationRule]] = None


class CountryRuleInDB(CountryRuleBase):
    """Country rule as stored in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    validation_rules: List[ValidationRule] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[ObjectId] = Field(None, description="User who created the rule")
    updated_by: Optional[ObjectId] = Field(None, description="User who last updated the rule")


class CountryRuleResponse(CountryRuleBase):
    """Country rule response schema"""
    id: str
    validation_rules: List[ValidationRule]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True
