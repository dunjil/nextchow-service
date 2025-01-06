from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from app.general.utils.helpers import PyObjectId
from app.vendors.schemas import Location, OperatingHours


class SignUpModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: str = Field(default="vendor")
    is_verified: bool = Field(default=False)
    is_onboarded: bool = Field(default=False)
    is_approved: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "jd@gmail.com",
                "password": "******************",
                "role": "vendor",
            }
        }


class VendorProfile(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: str
    store_name: str
    cover_picture: str
    profile_picture: str
    description: str
    location: Location
    address: str
    phone: str
    order_type: str
    profile_completed: bool = False
    is_verified: bool = False
    operating_hours: List[OperatingHours] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class VendorBankInformation(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    bank_code: str
    bank_name: str
    account_name: str
    account_number: str

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "bank_code": "033",
                "bank_name": "Opay Digital Services",
                "account_name": "John Doe",
                "account_number": "023423432",
            }
        }


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


class Menu(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    description: str
    price: float
    preparation_duration: str
    menu_picture: str
    is_available: bool = Field(default=False)
    category_id: str
    packaging_id: str

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Rice and Beans",
                "description": "Good for your Body",
                "user_id": "yyrtititit",
                "price": 2000,
                "preparation_duration": "25 minutes",
                "menu_picture": "https://cloudinary/images/home.jpg",
                "category_id": "cat534372711",
                "packaging_id": "tpack534372711",
            }
        }


class Category(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    name: str
    description: str

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Breakfast",
                "user_id": "23455324r42222",
                "description": "Good for your Body",
            }
        }


class Packaging(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    user_id: str
    price: float

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Rice and Beans",
                "description": "Good for your Body",
                "price": 2000,
            }
        }
