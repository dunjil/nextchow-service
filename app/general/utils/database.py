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
    MENU: str = "menu"
    VENDOR_PROFILE: str = "vendor_profile"
    ORDERS: str = "orders"
    VENDOR_OTP: str = "vendor_otp"
    MENU_PACKAGING:str="menu_packaging"
    MENU_CATEGORY:str="menu_category"
    CUSTOMER_USER: str = "customer_users"
    CUSTOMER_CART: str = "customer_cart"


client = motor_client.AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client["nextchow"]


def get_motor_client():
    return motor_client.AsyncIOMotorClient(os.getenv("MONGODB_URL"))


def get_database(client=Depends(get_motor_client)):
    return client["nextchow"]


# Create geospatial indexes for the ride locations
db[NEXTCHOW_COLLECTIONS.VENDOR_PROFILE].create_index([("location", GEOSPHERE)])
# db[NEXTCHOW_COLLECTIONS.RIDES].create_index([("end_location", GEOSPHERE)])
