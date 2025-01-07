import os
from datetime import datetime
from typing import List

import requests
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from geopy.distance import geodesic
from pymongo.errors import PyMongoError

from app.customers.models import *
from app.customers.schemas import CartPackSchema
from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.oauth_service import get_current_user

cart_router = APIRouter(prefix="/customer", tags=["Customer Cart Management"])


@cart_router.post("/cart/add-pack")
async def add_pack_to_cart(
    pack: CartPackSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Add a pack to the user's cart with comprehensive validations.
    """
    try:
        # Validate packaging exists
        if pack.packaging_id:
            packaging = await db[NEXTCHOW_COLLECTIONS.MENU_PACKAGING].find_one(
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

        # Validate menu items
        for item in pack.items:
            menu_item = await db[NEXTCHOW_COLLECTIONS.MENU].find_one(
                {"_id": ObjectId(item.menu_id)}
            )
            if not menu_item:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "message": f"Menu item {item.menu_id} not found",
                    },
                )

        # Fetch or create cart
        cart = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].find_one(
            {"user_id": str(user["_id"])}
        )
        if not cart:
            cart = {
                "user_id": str(user["_id"]),
                "packs": [],
                "total_price": 0.0,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

        # Limit cart size (optional - adjust as needed)
        if len(cart["packs"]) >= 20:  # Max 20 different packs
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": "Cart has reached maximum capacity",
                },
            )

        # Add pack to cart
        cart["packs"].append(pack.dict())
        cart["total_price"] = await calculate_cart_total(cart["packs"], db)
        cart["updated_at"] = datetime.now()

        # Save/update cart
        await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].update_one(
            {"user_id": str(user["_id"])}, {"$set": cart}, upsert=True
        )

        return {"success": True, "message": "Pack added to cart", "cart": cart}

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail= f"Database error: {str(e)}",
        )


@cart_router.get("/cart")
async def get_user_cart(
    user: dict = Depends(get_current_user), db=Depends(get_database)
):
    """
    Fetch the current user's cart.
    """
    try:
        cart = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].find_one(
            {"user_id": str(user["_id"])}
        )
        if not cart:
            return {"user_id": str(user["_id"]), "packs": [], "total_price": 0.0}
        return cart

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail= f"Database error: {str(e)}",
        )


@cart_router.delete("/cart/pack/{pack_index}")
async def remove_pack_from_cart(
    pack_index: int, user: dict = Depends(get_current_user), db=Depends(get_database)
):
    """
    Remove a specific pack from the user's cart.
    """
    try:
        cart = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].find_one(
            {"user_id": str(user["_id"])}
        )
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        try:
            del cart["packs"][pack_index]
        except IndexError:
            raise HTTPException(status_code=400, detail="Invalid pack index")

        cart["total_price"] = await calculate_cart_total(cart["packs"], db)
        cart["updated_at"] = datetime.now()

        await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].update_one(
            {"user_id": str(user["_id"])}, {"$set": cart}
        )
        return {"success": True, "message": "Pack removed from cart", "cart": cart}

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail= f"Database error: {str(e)}",
        )


@cart_router.post("/cart/checkout_and_initiate_payment")
async def checkout_and_initiate_payment(
    db=Depends(get_database),
    user: dict = Depends(get_current_user),
):
    """
    Convert the cart to an order, clear the cart, and initiate payment.
    """
    try:
        # Fetch the user's cart
        cart = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].find_one(
            {"user_id": str(user["_id"])}
        )
        if not cart or not cart["packs"]:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # Get menu and vendor details
        menu_id = cart["packs"][0]["items"][0].get(
            "menu_id"
        )  # Adjusted based on cart structure
        menu = await db[NEXTCHOW_COLLECTIONS.MENU].find_one({"_id": menu_id})
        if not menu:
            raise HTTPException(status_code=400, detail="Menu item not found")

        vendor = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"_id": menu.get("user_id")}
        )
        if not vendor or "location" not in vendor:
            raise HTTPException(
                status_code=400, detail="Vendor not found or location missing"
            )

        vendor_location = vendor.get("location")
        vendor_address = vendor.get("address", "Unknown")

        user_location = user.get("location")
        if not user_location:
            raise HTTPException(status_code=400, detail="User location is missing")

        # Calculate the estimated distance
        estimated_distance = geodesic(
            (vendor_location["coordinates"][1], vendor_location["coordinates"][0]),
            (user_location["coordinates"][1], user_location["coordinates"][0]),
        ).kilometers

        # Calculate total price
        total_price = await calculate_cart_total(cart["packs"], db)

        # Create an order
        order = {
            "user_id": str(user["_id"]),
            "pickup_address": vendor_address,
            "pickup_location": vendor_location,
            "delivery_address": user.get("address", ""),
            "delivery_location": user_location,
            "estimated_distance": round(estimated_distance, 2),
            "additional_info": user.get("additional_info", ""),
            "packs": cart["packs"],
            "total_price": total_price,
            "status": "Pending",
            "created_at": datetime.now(),
        }
        order_result = await db[NEXTCHOW_COLLECTIONS.ORDERS].insert_one(order)
        order_id = str(order_result.inserted_id)

        # Clear the cart
        await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].delete_one(
            {"user_id": str(user["_id"])}
        )

        # Prepare payment data
        payment_data = {
            "email": user.get("email"),
            "amount": total_price,
            "callback_url": "https://nextchow.com/verify",
            "channels": ["card"],
            "metadata": {
                "email": user.get("email"),
                "user_id": user.get("_id"),
                "order_id": order_id,
                "amount": total_price,
            },
        }

        # Initialize payment with Paystack
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {os.getenv('PAYMENT_SECRET_KEY')}",
            "Content-Type": "application/json",
        }
        response = requests.post(url=url, json=payment_data, headers=headers)

        if response.status_code in [200, 201]:
            payment_authorization_data = response.json().get("data")

            # Save payment details to the database
            payment = OrderPayment(
                order_id=order_id,
                user_id=user.get("_id"),
                amount=total_price,
                reference=payment_authorization_data.get("reference"),
                payment_method="credit_card",
                access_code=payment_authorization_data.get("access_code"),
            )
            await db[NEXTCHOW_COLLECTIONS.ORDER_PAYMENTS].insert_one(payment.dict())

            return {
                "status_code": status.HTTP_200_OK,
                "status": "success",
                "message": "Checkout and payment initialization successful",
                "order": order,
                "payment_url": payment_authorization_data.get("authorization_url"),
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail= "Failed to initialize payment",
            )

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e

# @cart_router.post("/cart/checkout")
# async def checkout(user: dict = Depends(get_current_user), db=Depends(get_database)):
#     """
#     Convert the cart to an order and clear the cart.
#     """
#     try:
#         cart = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].find_one(
#             {"user_id": str(user["_id"])}
#         )
#         if not cart or not cart["packs"]:
#             raise HTTPException(status_code=400, detail="Cart is empty")

#         # Create an order with more comprehensive user details
#         order = {
#             "user_id": str(user["_id"]),
#             "customer_name": user.get("first_name", "")
#             + " "
#             + user.get("last_name", ""),
#             "customer_phone": user.get("phone", ""),
#             "customer_address": user.get("address", ""),
#             "additional_info": user.get("additional_info", ""),
#             "packs": cart["packs"],
#             "total_price": cart["total_price"],
#             "status": "Pending",
#             "created_at": datetime.now(),
#         }

#         await db[NEXTCHOW_COLLECTIONS.ORDERS].insert_one(order)

#         # Clear the cart
#         await db[NEXTCHOW_COLLECTIONS.CUSTOMER_CART].delete_one(
#             {"user_id": str(user["_id"])}
#         )

#         return {"success": True, "message": "Checkout successful", "order": order}

#     except PyMongoError as e:
#         raise HTTPException(
#             status_code=500,
#             detail= f"Database error: {str(e)}"},
#         )


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
                packaging = await db["packaging"].find_one(
                    {"_id": ObjectId(pack["packaging_id"])}
                )
                if packaging:
                    pack_total += packaging["price"]
            total_price += pack_total
        return total_price
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Database error in total calculation: {str(e)}",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Unexpected error in total calculation: {str(e)}",
            },
        )


# TODO: Confirm order payment
# TODO: Assign Order to Riders

# @cart_router.post("/initiate_payment")
# async def initiate_payment(
#     data: OrderPaymentSchema,
#     user: dict = Depends(get_current_user),
#     db=Depends(get_database),
# ):
#     data = jsonable_encoder(data)
#     total_amount = data.get("total_amount")

#     # data = jsonable_encoder(data)
#     payment_data = {
#         "email": user.get("email"),
#         "amount": total_amount,
#         "callback_url": "https://nextchow.com/verify",
#         "channels": ["card"],
#         "metadata": {
#             "email": user.get("email"),
#             "user_id": user.get("_id"),
#             "order_id": data.get("order_id"),
#             "amount": total_amount,
#         },
#     }

#     url = "https://api.paystack.co/transaction/initialize"
#     headers = {
#         "Authorization": f"Bearer {os.getenv('PAYMENT_SECRET_KEY')}",
#         "Content-Type": "application/json",
#     }

#     response = requests.post(url=url, json=payment_data, headers=headers)
#     if response.status_code in [200, 201]:
#         payment_authorization_data = response.json().get("data")
#         payment = OrderPayment(
#             order_id=data.get("order_id"),
#             user_id=user.get("_id"),
#             amount=total_amount,
#             reference=payment_authorization_data.get("reference"),
#             payment_method="credit_card",
#             access_code=payment_authorization_data.get("access_code"),
#         )

#         await db[NEXTCHOW_COLLECTIONS.ORDER_PAYMENTS].insert_one(payment.dict())
#         return {
#             "status_code": status.HTTP_200_OK,
#             "status": "success",
#             "message": "Payment URL generated successfully",
#             "data": payment_authorization_data,
#         }
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail= "Failed to initialize payment"},
#         )
