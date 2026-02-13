from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId

class Country(str, Enum):
    BRAZIL = "Brazil"
    MEXICO = "Mexico"
    PORTUGAL = "Portugal"
    SPAIN = "Spain"
    ITALY = "Italy"
    COLOMBIA = "Colombia"

class CreditRequestStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class BankInformation(BaseModel):
    """Bank information from provider"""
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_type: Optional[str] = None
    routing_number: Optional[str] = None
    iban: Optional[str] = None
    swift: Optional[str] = None
    provider_data: Optional[dict] = None  # Raw data from provider

class CreditRequestBase(BaseModel):
    country: Country
    full_name: str = Field(..., min_length=1, max_length=200)
    identity_document: str = Field(..., min_length=1, max_length=50)
    requested_amount: float = Field(..., gt=0)
    monthly_income: float = Field(..., gt=0)

class CreditRequestCreate(CreditRequestBase):
    """Schema for creating a credit request"""
    pass

class CreditRequestInDB(CreditRequestBase):
    """Credit request as stored in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_id: ObjectId  # Reference to user who created the request
    request_date: datetime = Field(default_factory=datetime.utcnow)
    status: CreditRequestStatus = CreditRequestStatus.PENDING
    bank_information: Optional[BankInformation] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CreditRequestResponse(CreditRequestBase):
    """Credit request response schema"""
    id: str
    user_id: str
    request_date: datetime
    status: CreditRequestStatus
    bank_information: Optional[BankInformation] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CreditRequestUpdate(BaseModel):
    """Schema for updating a credit request"""
    status: Optional[CreditRequestStatus] = None
    bank_information: Optional[BankInformation] = None
