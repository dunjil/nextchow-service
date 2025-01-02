import os
from dataclasses import dataclass

import motor.motor_asyncio as motor_client
from dotenv import load_dotenv
from fastapi import Depends
from pymongo import GEOSPHERE

load_dotenv()


@dataclass
class NEXTCHOW_COLLECTIONS:
    VENDOR_USER: str = "vendor_users"
    VENDOR_BANK_ACCOUNT: str = "vendor_bank_account"
    VENDOR_SETTLEMENTS: str = "vendor_settlements"
    MENU: str = "menu"
    VENDOR_PROFILE: str = "vendor_profile"
    ORDERS: str = "orders"
    VENDOR_OTP: str = "vendor_otp"
    MENU_PACKAGING: str = "menu_packaging"
    ORDER_PAYMENTS: str = "order_payments"
    MENU_CATEGORY: str = "menu_category"
    CUSTOMER_USER: str = "customer_users"
    CUSTOMER_CART: str = "customer_cart"
    RIDER_USER: str = "rider_users"
    RIDER_BANK_ACCOUNT: str = "rider_bank_account"
    RIDER_SETTLEMENTS: str = "rider_settlements"


client = motor_client.AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client["nextchow"]


def get_motor_client():
    return motor_client.AsyncIOMotorClient(os.getenv("MONGODB_URL"))


def get_database(client=Depends(get_motor_client)):
    return client["nextchow"]


# Create geospatial indexes for the ride locations
db[NEXTCHOW_COLLECTIONS.VENDOR_PROFILE].create_index([("location", GEOSPHERE)])
# db[NEXTCHOW_COLLECTIONS.RIDES].create_index([("end_location", GEOSPHERE)])
