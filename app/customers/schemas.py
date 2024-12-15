from datetime import datetime
from typing import Optional,List
from bson import ObjectId
from pydantic import BaseModel, Field,EmailStr
from app.general.utils.helpers import PyObjectId

class Location(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(default_factory=lambda: [0.0, 0.0])


class SignUpSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    phone:str
    password:str
    role:str
    location:Location
    address: str
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
                "phone":"+23470665543",
                "role":"customer",
                "location": {
                    "type": "Point",
                    "coordinates": [8.8940691, 7.1860402],
                },
                "address": "Zarmaganda Rayfield Road Jos",
            }
        }

class LoginSchema(BaseModel):
    email: EmailStr
    password:str

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


class OTPVerification(BaseModel):
    email: EmailStr
    otp: str


class CartItemSchema(BaseModel):
    menu_id: str
    quantity: int

    class Config:
        json_schema_extra = {
            "example": {
                "menu_id": "menu534372711",
                "quantity": 2
            }
        }


class CartPackSchema(BaseModel):
    items: List[CartItemSchema]
    packaging_id: Optional[str]  # Packaging is optional for a pack

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"menu_id": "menu534372711", "quantity": 2},
                    {"menu_id": "menu987654321", "quantity": 1}
                ],
                "packaging_id": "pack534372711"
            }
        }


class UserCartSchema(BaseModel):
    user_id: str
    packs: List[CartPackSchema]
    total_price: float = 0.0

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "user_id": "user12345",
                "packs": [
                    {
                        "items": [
                            {"menu_id": "menu534372711", "quantity": 2},
                            {"menu_id": "menu987654321", "quantity": 1}
                        ],
                        "packaging_id": "pack534372711"
                    },
                    {
                        "items": [
                            {"menu_id": "menu112233445", "quantity": 1}
                        ],
                        "packaging_id": "pack987654321"
                    }
                ],
                "total_price": 6400.0
            }
        }


class PasswordResetRequestSchema(BaseModel):
    email: EmailStr

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "jd@gmail.com"
    
            }
        }
class PasswordResetSchema(BaseModel):
    email: EmailStr
    new_password:str

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
                "current_password":"**************",
                "new_password": "******************",
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
                    }
                ]
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
                            {"menu_id": "menu123456789", "quantity": 1}
                        ]
                    },
                    {
                        "packaging_id": "pack987654321",
                        "items": [
                            {"menu_id": "menu112233445", "quantity": 3}
                        ]
                    }
                ],
                "total_price": 7500.0
            }
        }


from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "Pending"
    PREPARING = "Preparing"
    READY = "Ready"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"