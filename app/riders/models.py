from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from app.general.utils.helpers import PyObjectId


class RiderProfile(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: str
    profile_picture: str
    phone: str
    profile_completed: bool = False
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class BankAccount(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    account_number: str = Field(..., description="The bank account number")
    user_id: str = Field(
        ..., description="The ID of the user associated with the account"
    )
    bank_code: str = Field(..., description="The bank's code")
    bank_name: str = Field(..., description="The name of the bank")
    account_name: str = Field(..., description="The name on the bank account")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "account_number": "0193274682",
                "user_id": "1234567890",
                "bank_code": "044",
                "bank_name": "First Bank",
                "account_name": "Sunshine Studios",
            }
        }
