from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import PyMongoError

from app.customers.schemas import (  # Assuming you have an OrderSchema
    OrderPaymentSchema,
    OrderSchema,
)
from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.oauth_service import get_current_user

customer_order_router = APIRouter(prefix="/customer", tags=["Customer Orders"])


@customer_order_router.get("/orders")
async def fetch_customer_orders(
    user: dict = Depends(get_current_user), db=Depends(get_database)
):
    """
    Fetch all orders for the current customer.
    """
    try:
        # Find orders for the current customer
        orders = (
            await db[NEXTCHOW_COLLECTIONS.ORDERS]
            .find({"customer_id": str(user.get("_id"))})
            .to_list(length=100)
        )

        # Populate menu and packaging details for each pack
        for order in orders:
            for pack in order.get("packs", []):
                # Fetch packaging details
                if pack.get("packaging_id"):
                    pack["packaging"] = await db[
                        NEXTCHOW_COLLECTIONS.MENU_PACKAGING
                    ].find_one({"_id": ObjectId(pack["packaging_id"])})

                # Fetch menu item details
                for item in pack.get("items", []):
                    item["menu"] = await db[NEXTCHOW_COLLECTIONS.MENU].find_one(
                        {"_id": ObjectId(item["menu_id"])}
                    )

        return orders
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail= f"Database error: {str(e)}",
        )


@customer_order_router.get("/orders/{order_id}")
async def get_customer_order_details(
    order_id: str, user: dict = Depends(get_current_user), db=Depends(get_database)
):
    """
    Fetch details of a specific order for the current customer.
    """
    try:
        # Find the specific order for the current customer
        order = await db[NEXTCHOW_COLLECTIONS.ORDERS].find_one(
            {"_id": ObjectId(order_id), "customer_id": str(user.get("_id"))}
        )

        if not order:
            raise HTTPException(
                status_code=404, detail= "Order not found"
            )

        # Populate menu and packaging details
        for pack in order.get("packs", []):
            # Fetch packaging details
            if pack.get("packaging_id"):
                pack["packaging"] = await db[
                    NEXTCHOW_COLLECTIONS.MENU_PACKAGING
                ].find_one({"_id": ObjectId(pack["packaging_id"])})

            # Fetch menu item details
            for item in pack.get("items", []):
                item["menu"] = await db[NEXTCHOW_COLLECTIONS.MENU].find_one(
                    {"_id": ObjectId(item["menu_id"])}
                )

        return order
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail= f"Database error: {str(e)}",
        )


@customer_order_router.get("/orders/by-status/{status}")
async def fetch_customer_orders_by_status(
    status: str, user: dict = Depends(get_current_user), db=Depends(get_database)
):
    """
    Fetch customer orders by specific status.
    """
    try:
        orders = (
            await db[NEXTCHOW_COLLECTIONS.ORDERS]
            .find({"customer_id": str(user.get("_id")), "status": status})
            .to_list(length=100)
        )

        # Populate menu and packaging details
        for order in orders:
            for pack in order.get("packs", []):
                # Fetch packaging details
                if pack.get("packaging_id"):
                    pack["packaging"] = await db[
                        NEXTCHOW_COLLECTIONS.MENU_PACKAGING
                    ].find_one({"_id": ObjectId(pack["packaging_id"])})

                # Fetch menu item details
                for item in pack.get("items", []):
                    item["menu"] = await db[NEXTCHOW_COLLECTIONS.MENU].find_one(
                        {"_id": ObjectId(item["menu_id"])}
                    )

        return orders
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail= f"Database error: {str(e)}",
        )


@customer_order_router.post("/reorder/{order_id}")
async def reorder_previous_order(
    order_id: str, user: dict = Depends(get_current_user), db=Depends(get_database)
):
    """
    Create a new order based on a previous order.
    """
    try:
        # Find the original order
        original_order = await db[NEXTCHOW_COLLECTIONS.ORDERS].find_one(
            {"_id": ObjectId(order_id), "customer_id": str(user.get("_id"))}
        )

        if not original_order:
            raise HTTPException(
                status_code=404,
                detail= "Original order not found",
            )

        # Prepare new order data
        new_order = {
            "customer_id": str(user.get("_id")),
            "packs": original_order.get("packs", []),
            "total_price": original_order.get("total_price", 0),
            "status": "Pending",
            "created_at": datetime.now(),
        }

        # Insert the new order
        result = await db[NEXTCHOW_COLLECTIONS.ORDERS].insert_one(new_order)

        return {
            "success": True,
            "message": "Order recreated successfully",
            "order_id": str(result.inserted_id),
        }
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail= f"Database error: {str(e)}",
        )


@customer_order_router.post("/cancel-order/{order_id}")
async def cancel_order(
    order_id: str, user: dict = Depends(get_current_user), db=Depends(get_database)
):
    """
    Cancel a pending order.
    """
    try:
        # Update order status to cancelled
        result = await db[NEXTCHOW_COLLECTIONS.ORDERS].update_one(
            {
                "_id": ObjectId(order_id),
                "customer_id": str(user.get("_id")),
                "status": "Pending",
            },
            {"$set": {"status": "Cancelled"}},
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail= "Order cannot be cancelled",
            )

        return {"success": True, "message": "Order cancelled successfully"}
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail= f"Database error: {str(e)}",
        )
