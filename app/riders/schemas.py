from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from app.general.utils.helpers import PyObjectId


class Location(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(default_factory=lambda: [0.0, 0.0])


class OperatingHours(BaseModel):
    day: str
    open_time: Optional[str] = None  # Time in "HH:MM" format
    close_time: Optional[str] = None  # Time in "HH:MM" format

    class Config:
        schema_extra = {
            "example": {"day": "Monday", "open_time": "08:00", "close_time": "18:00"}
        }


class SignUpSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    vehicle_type: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "jd@gmail.com",
                "password": "******************",
                "vehicle_type": "bicycle",
            }
        }


class BusinessProfileSchema(BaseModel):
    store_name: str
    description: str
    location: Location
    address: str
    phone: str
    cover_picture: str
    profile_picture: str
    order_type: str
    operating_hours: List[OperatingHours] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "store_name": "Jenny's kitchen",
                "description": "Stomach happiness",
                "location": {
                    "type": "Point",
                    "coordinates": [8.8940691, 7.1860402],
                },
                "address": "Zarmaganda Rayfield Road Jos",
                "phone": "+23461046672",
                "order_type": "Both",
                "cover_picture": "https://cloudinary/images/home.jpg",
                "profile_picture": "https://cloudinary/images/home.jpg",
                "operating_hours": [
                    {"day": "Monday", "open_time": "08:00", "close_time": "18:00"},
                    {"day": "Tuesday", "open_time": "08:00", "close_time": "18:00"},
                    {"day": "Sunday", "open_time": None, "close_time": None},
                ],
            }
        }


class LoginSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "jd@gmail.com",
                "password": "******************",
            }
        }


class PasswordResetRequestSchema(BaseModel):
    email: EmailStr

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {"example": {"email": "jd@gmail.com"}}


class PasswordResetSchema(BaseModel):
    email: EmailStr
    new_password: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "jd@gmail.com",
                "new_password": "******************",
            }
        }


class ChangePasswordSchema(BaseModel):
    current_password: str
    new_password: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "current_password": "**************",
                "new_password": "******************",
            }
        }


class BankInformationSchema(BaseModel):
    bank_code: str
    bank_name: str
    account_name: str
    account_number: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "bank_code": "033",
                "bank_name": "Opay Digital Services",
                "account_name": "John Doe",
                "account_number": "023423432",
            }
        }


class MenuSchema(BaseModel):
    name: str
    description: str
    price: float
    preparation_duration: str
    menu_picture: str
    category_id: str
    packaging_id: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Rice and Beans",
                "description": "Good for your Body",
                "price": 2000,
                "preparation_duration": "25 minutes",
                "menu_picture": "https://cloudinary/images/home.jpg",
                "category_id": "cat534372711",
                "packaging_id": "tpack534372711",
            }
        }


class CategorySchema(BaseModel):
    name: str
    description: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Breakfast",
                "description": "Good for your Body",
            }
        }


class PackagingSchema(BaseModel):
    name: str
    description: str
    price: float

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Leather Bag",
                "description": "Good and esy to carry, reusable",
                "price": 400,
            }
        }


class OTPVerification(BaseModel):
    email: EmailStr
    otp: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "johnd@gmail.com",
                "otp": "123421",
            }
        }


class PackItemSchema(BaseModel):
    menu_id: str
    quantity: int

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "menu_id": "menu534372711",
                "quantity": 2,
            }
        }


class PackSchema(BaseModel):
    packaging_id: str
    items: List[PackItemSchema]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "packaging_id": "pack534372711",
                "items": [
                    {
                        "menu_id": "menu534372711",
                        "quantity": 2,
                    },
                    {
                        "menu_id": "menu123456789",
                        "quantity": 1,
                    },
                ],
            }
        }


class OrderSchema(BaseModel):
    customer_name: str
    customer_phone: str
    customer_address: str
    packs: List[PackSchema]
    total_price: float

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "customer_name": "Jane Doe",
                "customer_phone": "+123456789",
                "customer_address": "123 Main Street",
                "packs": [
                    {
                        "packaging_id": "pack534372711",
                        "items": [
                            {"menu_id": "menu534372711", "quantity": 2},
                            {"menu_id": "menu123456789", "quantity": 1},
                        ],
                    },
                    {
                        "packaging_id": "pack987654321",
                        "items": [{"menu_id": "menu112233445", "quantity": 3}],
                    },
                ],
                "total_price": 7500.0,
            }
        }


class BankAccountSchema(BaseModel):
    account_name: str = Field()
    bank_code: str = Field()
    bank_name: str = Field()
    account_number: str = Field()

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "account_name": "Sunshine Studios",
                "bank_code": "044",
                "bank_name": "First Bank",
                "account_number": "0193274682",
            }
        }


class ResolveBankAccountSchema(BaseModel):
    bank_code: str = Field()
    account_number: str = Field()

    class Config:
        allowed_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "bank_code": "044",
                "account_number": "4034555669",
            }
        }


from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "Pending"
    PREPARING = "Preparing"
    READY = "Ready"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
