# TODO: Get Vendors Close to the customers' location
# TODO: Get the menu of that vendor by the vendor's ID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.errors import PyMongoError

from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.helpers import *
from app.general.utils.oauth_service import get_current_user
from app.vendors.models import *
from app.vendors.schemas import *

customer_vendor_router = APIRouter(prefix="/customer-vendor", tags=["Customer's Vendor"])



# Fetch all vendors
@customer_vendor_router.get("/vendors")
async def fetch_vendors(
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        vendors = (
            await db[NEXTCHOW_COLLECTIONS.MENU]
            .find()
            .to_list()
        )
        return {"success": True, "data": jsonable_encoder(vendors)}
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e

# Fetch all menus for a vendor
@customer_vendor_router.get("/vendor/{vendor_id}/menus")
async def fetch_menu(
    vendor_id: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        menus = (
            await db[NEXTCHOW_COLLECTIONS.MENU]
            .find({"user_id": vendor_id})
            .to_list(length=100)
        )
        return {"success": True, "data": jsonable_encoder(menus)}
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e