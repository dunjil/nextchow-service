from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import PyMongoError
from bson import ObjectId

from app.customers.schemas import CartPackSchema, UserCartSchema
from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.oauth_service import get_current_user

cart_router = APIRouter(prefix="/customer", tags=["Customer Cart Management"])

@cart_router.post("/cart/add-pack")
async def add_pack_to_cart(
    pack: CartPackSchema, 
    user: dict = Depends(get_current_user), 
    db=Depends(get_database)
):
    """
    Add a pack to the user's cart with comprehensive validations.
    """
    try:
        # Validate packaging exists
        if pack.packaging_id:
            packaging = await db[NEXTCHOW_COLLECTIONS.MENU_PACKAGING].find_one({"_id": ObjectId(pack.packaging_id)})
            if not packaging:
                raise HTTPException(
                    status_code=400,
                    detail={"success": False, "message": f"Packaging {pack.packaging_id} not found"}
                )

        # Validate menu items
        for item in pack.items:
            menu_item = await db[NEXTCHOW_COLLECTIONS.MENU].find_one({"_id": ObjectId(item.menu_id)})
            if not menu_item:
                raise HTTPException(
                    status_code=400,
                    detail={"success": False, "message": f"Menu item {item.menu_id} not found"}
                )

        # Fetch or create cart
        cart = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].find_one({"user_id": str(user['_id'])})
        if not cart:
            cart = {
                "user_id": str(user['_id']), 
                "packs": [], 
                "total_price": 0.0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

        # Limit cart size (optional - adjust as needed)
        if len(cart["packs"]) >= 20:  # Max 20 different packs
            raise HTTPException(
                status_code=400,
                detail={"success": False, "message": "Cart has reached maximum capacity"}
            )

        # Add pack to cart
        cart["packs"].append(pack.dict())
        cart["total_price"] = await calculate_cart_total(cart["packs"], db)
        cart["updated_at"] = datetime.now()

        # Save/update cart
        await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].update_one(
            {"user_id": str(user['_id'])}, 
            {"$set": cart}, 
            upsert=True
        )

        return {"success": True, "message": "Pack added to cart", "cart": cart}

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"}
        )

@cart_router.get("/cart")
async def get_user_cart(
    user: dict = Depends(get_current_user), 
    db=Depends(get_database)
):
    """
    Fetch the current user's cart.
    """
    try:
        cart = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].find_one({"user_id": str(user['_id'])})
        if not cart:
            return {"user_id": str(user['_id']), "packs": [], "total_price": 0.0}
        return cart

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"}
        )

@cart_router.delete("/cart/pack/{pack_index}")
async def remove_pack_from_cart(
    pack_index: int, 
    user: dict = Depends(get_current_user), 
    db=Depends(get_database)
):
    """
    Remove a specific pack from the user's cart.
    """
    try:
        cart = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].find_one({"user_id": str(user['_id'])})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        try:
            del cart["packs"][pack_index]
        except IndexError:
            raise HTTPException(status_code=400, detail="Invalid pack index")

        cart["total_price"] = await calculate_cart_total(cart["packs"], db)
        cart["updated_at"] = datetime.now()

        await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].update_one(
            {"user_id": str(user['_id'])}, 
            {"$set": cart}
        )
        return {"success": True, "message": "Pack removed from cart", "cart": cart}

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"}
        )

# The calculate_cart_total function remains the same as in the original implementation

@cart_router.post("/cart/checkout")
async def checkout(
    user: dict = Depends(get_current_user), 
    db=Depends(get_database)
):
    """
    Convert the cart to an order and clear the cart.
    """
    try:
        cart = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].find_one({"user_id": str(user['_id'])})
        if not cart or not cart["packs"]:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # Create an order with more comprehensive user details
        order = {
            "customer_id": str(user['_id']),
            "customer_name": user.get('first_name', '') + ' ' + user.get('last_name', ''),
            "customer_phone": user.get('phone', ''),
            "customer_address": user.get('address', ''),
            "packs": cart["packs"],
            "total_price": cart["total_price"],
            "status": "Pending",
            "created_at": datetime.now()
        }
        
        await db[NEXTCHOW_COLLECTIONS.ORDERS].insert_one(order)

        # Clear the cart
        await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].delete_one({"user_id": str(user['_id'])})

        return {"success": True, "message": "Checkout successful", "order": order}

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"}
        )
    

async def calculate_cart_total(packs: List[CartPackSchema], db) -> float:
    try:
        total_price = 0.0
        for pack in packs:
            pack_total = 0.0
            for item in pack["items"]:
                menu = await db["menu"].find_one({"_id": ObjectId(item["menu_id"])})
                if menu:
                    pack_total += menu["price"] * item["quantity"]
            if pack["packaging_id"]:
                packaging = await db["packaging"].find_one({"_id": ObjectId(pack["packaging_id"])})
                if packaging:
                    pack_total += packaging["price"]
            total_price += pack_total
        return total_price
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error in total calculation: {str(e)}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Unexpected error in total calculation: {str(e)}"}
        )