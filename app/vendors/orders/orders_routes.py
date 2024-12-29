from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.errors import PyMongoError

from app.general.utils.database import get_database
from app.general.utils.helpers import *
from app.vendors.models import *
from app.vendors.schemas import *

order_router = APIRouter(prefix="/vendor", tags=["Vendor Orders"])


@order_router.post("/orders")
async def create_order(order_data: OrderSchema, db=Depends(get_database)):
    try:
        # Validate menu and packaging references
        for pack in order_data.packs:
            packaging = await db["packaging"].find_one(
                {"_id": ObjectId(pack.packaging_id)}
            )
            if not packaging:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "message": f"Packaging {pack.packaging_id} not found",
                    },
                )
            for item in pack.items:
                menu = await db["menu"].find_one({"_id": ObjectId(item.menu_id)})
                if not menu:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "success": False,
                            "message": f"Menu item {item.menu_id} not found",
                        },
                    )

        # Insert the order
        order = jsonable_encoder(order_data)
        result = await db["orders"].insert_one(order)

        if result.inserted_id:
            return {"success": True, "message": "Order created successfully"}
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )


@order_router.get("/orders", response_model=List[OrderSchema])
async def fetch_orders(db=Depends(get_database)):
    try:
        orders = await db["orders"].find().to_list(length=100)

        # Populate menu and packaging details for each pack
        for order in orders:
            for pack in order["packs"]:
                pack["packaging"] = await db["packaging"].find_one(
                    {"_id": ObjectId(pack["packaging_id"])}
                )
                for item in pack["items"]:
                    item["menu"] = await db["menu"].find_one(
                        {"_id": ObjectId(item["menu_id"])}
                    )

        return orders
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )


@order_router.put("/orders/{order_id}")
async def update_order(
    order_id: str, order_data: OrderSchema, db=Depends(get_database)
):
    try:
        # Validate menu and packaging references
        for pack in order_data.packs:
            packaging = await db["packaging"].find_one({"_id": pack.packaging_id})
            if not packaging:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "message": f"Packaging {pack.packaging_id} not found",
                    },
                )
            for item in pack.items:
                menu = await db["menu"].find_one({"_id": item.menu_id})
                if not menu:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "success": False,
                            "message": f"Menu item {item.menu_id} not found",
                        },
                    )

        # Update the order
        updated_order = jsonable_encoder(order_data)
        result = await db["orders"].update_one(
            {"_id": order_id}, {"$set": updated_order}
        )

        if result.modified_count:
            return {"success": True, "message": "Order updated successfully"}
        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Order not found or no changes made"},
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )


@order_router.delete("/orders/{order_id}")
async def delete_order(order_id: str, db=Depends(get_database)):
    try:
        result = await db["orders"].delete_one({"_id": ObjectId(order_id)})
        if result.deleted_count:
            return {"success": True, "message": "Order deleted successfully"}
        raise HTTPException(
            status_code=404, detail={"success": False, "message": "Order not found"}
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )


@order_router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str, status: OrderStatus, db=Depends(get_database)
):
    """
    Update the status of an order.
    """
    try:
        # Validate the status and update the order
        result = await db["orders"].update_one(
            {"_id": ObjectId(order_id)}, {"$set": {"status": status}}
        )

        if result.modified_count:
            return {"success": True, "message": f"Order status updated to {status}"}

        raise HTTPException(
            status_code=404,
            detail={"success": False, "message": "Order not found or status unchanged"},
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )


@order_router.get("/orders/by-status/{status}", response_model=List[OrderSchema])
async def fetch_orders_by_status(status: OrderStatus, db=Depends(get_database)):
    """
    Fetch all orders with a specific status.
    """
    try:
        orders = await db["orders"].find({"status": status}).to_list(length=100)
        return orders
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )
