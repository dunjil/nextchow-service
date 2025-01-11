from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.errors import PyMongoError

from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.helpers import *
from app.general.utils.oauth_service import get_current_user
from app.vendors.models import *
from app.vendors.schemas import *

menus_router = APIRouter(prefix="/vendor", tags=["Vendor Menu"])


# Add ride endpoint
@menus_router.post("/add-menu")
async def add_ride(
    menu_data: MenuSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        menu_data = jsonable_encoder(menu_data)
        new_menu = Menu(**menu_data, user_id=user.get("_id"))
        new_menu = jsonable_encoder(new_menu)
        result = await db[NEXTCHOW_COLLECTIONS.MENU].insert_one(new_menu)
        if result.inserted_id:
            return {"success": True, "message": "Menu successfully added"}
        raise HTTPException(
            status_code=500,
            detail="Menu could not be added",
        )

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Fetch all menus for a vendor
@menus_router.get("/menus")
async def fetch_menus(
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        menus = (
            await db[NEXTCHOW_COLLECTIONS.MENU]
            .find({"user_id": user.get("_id")})
            .to_list(length=100)
        )
        return {"success": True, "data": menus}
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Update menu endpoint
@menus_router.put("/menu/{menu_id}")
async def update_menu(
    menu_id: str,
    menu_data: Menu,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        menu_data = jsonable_encoder(menu_data)
        result = await db[NEXTCHOW_COLLECTIONS.VENDOR_MENU].update_one(
            {"_id": ObjectId(menu_id), "user_id": user.get("_id")}, {"$set": menu_data}
        )
        if result.modified_count:
            return {"success": True, "message": "Menu successfully updated"}
        raise HTTPException(
            status_code=404,
            detail="Menu not found or no changes made",
        )

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Delete menu endpoint
@menus_router.delete("/menu/{menu_id}")
async def delete_menu(
    menu_id: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        result = await db[NEXTCHOW_COLLECTIONS.MENU].delete_one(
            {"_id": ObjectId(menu_id), "user_id": user.get("_id")}
        )
        if result.deleted_count:
            return {"success": True, "message": "Menu successfully deleted"}
        raise HTTPException(
            status_code=404,
            detail="Menu not found",
        )

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


categories_router = APIRouter(prefix="/vendor", tags=["Vendor Menu Categories"])
packaging_router = APIRouter(prefix="/vendor", tags=["Vendor Menu Packaging"])


# Add category endpoint
@categories_router.post("/add-category")
async def add_category(
    category_data: CategorySchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        category_data = jsonable_encoder(category_data)
        new_category = Category(**category_data, user_id=user.get("_id"))
        new_category = jsonable_encoder(new_category)
        result = await db[NEXTCHOW_COLLECTIONS.MENU_CATEGORY].insert_one(new_category)
        if result.inserted_id:
            return {"success": True, "message": "Category successfully added"}
        raise HTTPException(
            status_code=500,
            detail="Category could not be added",
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Fetch all categories for a vendor
@categories_router.get("/categories")
async def fetch_categories(
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        categories = (
            await db[NEXTCHOW_COLLECTIONS.MENU_CATEGORY]
            .find({"user_id": user.get("_id")})
            .to_list(length=100)
        )
        return {"success": True, "data": categories}
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Update category endpoint
@categories_router.put("/category/{category_id}")
async def update_category(
    category_id: str,
    category_data: CategorySchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        category_data = jsonable_encoder(category_data)
        result = await db[NEXTCHOW_COLLECTIONS.MENU_CATEGORY].update_one(
            {"_id": ObjectId(category_id), "user_id": user.get("_id")},
            {"$set": category_data},
        )
        if result.modified_count:
            return {"success": True, "message": "Category successfully updated"}
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "Category not found or no changes made",
            },
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Delete category endpoint
@categories_router.delete("/category/{category_id}")
async def delete_category(
    category_id: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        result = await db[NEXTCHOW_COLLECTIONS.MENU_CATEGORY].delete_one(
            {"_id": ObjectId(category_id), "user_id": user.get("_id")}
        )
        if result.deleted_count:
            return {"success": True, "message": "Category successfully deleted"}
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Add packaging endpoint
@packaging_router.post("/add-packaging")
async def add_packaging(
    packaging_data: PackagingSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        packaging_data = jsonable_encoder(packaging_data)
        new_packaging = Packaging(**packaging_data, user_id=user.get("_id"))
        new_packaging = jsonable_encoder(new_packaging)
        result = await db[NEXTCHOW_COLLECTIONS.MENU_PACKAGING].insert_one(new_packaging)
        if result.inserted_id:
            return {"success": True, "message": "Packaging successfully added"}
        raise HTTPException(
            status_code=500,
            detail="Packaging could not be added",
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Fetch all packaging for a vendor
@packaging_router.get("/packaging")
async def fetch_packaging(
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        packaging = (
            await db[NEXTCHOW_COLLECTIONS.MENU_PACKAGING]
            .find({"user_id": user.get("_id")})
            .to_list(length=100)
        )
        return {"success": True, "data": packaging}
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Update packaging endpoint
@packaging_router.put("/packaging/{packaging_id}")
async def update_packaging(
    packaging_id: str,
    packaging_data: PackagingSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        packaging_data = jsonable_encoder(packaging_data)
        result = await db[NEXTCHOW_COLLECTIONS.MENU_PACKAGING].update_one(
            {"_id": ObjectId(packaging_id), "user_id": user.get("_id")},
            {"$set": packaging_data},
        )
        if result.modified_count:
            packaging = await db[NEXTCHOW_COLLECTIONS.MENU_PACKAGING].find_one(
                {"user_id": user.get("_id")}
            )

            return {
                "success": True,
                "message": "Packaging successfully updated",
                "data": packaging,
            }
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "Packaging not found or no changes made",
            },
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


# Delete packaging endpoint
@packaging_router.delete("/packaging/{packaging_id}")
async def delete_packaging(
    packaging_id: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        result = await db[NEXTCHOW_COLLECTIONS.MENU_PACKAGING].delete_one(
            {"_id": ObjectId(packaging_id), "user_id": user.get("_id")}
        )
        if result.deleted_count:
            return {"success": True, "message": "Packaging successfully deleted"}
        raise HTTPException(
            status_code=404,
            detail="Packaging not found",
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e
