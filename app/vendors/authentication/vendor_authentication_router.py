from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.errors import PyMongoError

from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.helpers import *
from app.general.utils.oauth_service import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.vendors.models import *
from app.vendors.models import SignUpModel
from app.vendors.schemas import *
from app.vendors.schemas import LoginSchema, OTPVerification, SignUpSchema

vendor_auth_router = APIRouter(prefix="/vendor", tags=["Vendor Authentication"])


@vendor_auth_router.post("/signup")
async def vendor_signup(signup_data: SignUpSchema, db=Depends(get_database)):
    try:
        # Check if user already exists
        existing_user = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"email": signup_data.email}
        )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "message": "Email already registered"},
            )

        # Hash the password
        hashed_password = get_password_hash(signup_data.password)

        # Prepare user data
        user_data = jsonable_encoder(SignUpModel(**signup_data.dict()))

        # Generate OTP
        # otp = generate_otp()
        user_data.update(
            {
                "password": hashed_password,
                "otp": get_password_hash(
                    "123456"
                ),  # Replace with `generate_otp()` if needed
                "otp_created_at": datetime.now(),
            }
        )
        # data=jsonable_encoder(jsonable_encoder)

        # Insert user with OTP
        result = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].insert_one(user_data)

        # Send OTP via email
        # await send_reg_otp_mail(signup_data.email, otp)

        return {
            "success": True,
            "message": "Signup successful. OTP sent to your email.",
            "user_id": str(result.inserted_id),
        }

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Unexpected error: {str(e)}"},
        )


@vendor_auth_router.post("/verify-otp")
async def verify_otp(otp_verification: OTPVerification, db=Depends(get_database)):
    try:
        # Find user by email
        user = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"email": otp_verification.email}
        )

        if not user:
            raise HTTPException(
                status_code=404, detail={"success": False, "message": "User not found"}
            )

        # Check if OTP is valid and not expired
        otp_hash = user.get("otp")
        otp_created_at = user.get("otp_created_at")

        if not otp_hash or not otp_created_at:
            raise HTTPException(
                status_code=400,
                detail="No OTP exists for this user",
            )

        # Check OTP expiration (e.g., 15 minutes)
        if (datetime.now() - otp_created_at).total_seconds() > 900:
            raise HTTPException(
                status_code=400, detail= "OTP has expired"
            )

        # Verify OTP
        if not verify_password(otp_verification.otp, otp_hash):
            raise HTTPException(
                status_code=400, detail= "Invalid OTP"
            )

        # Mark user as verified
        await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].update_one(
            {"email": otp_verification.email},
            {"$set": {"is_verified": True}, "$unset": {"otp": 1, "otp_created_at": 1}},
        )

        # Create access token
        access_token = create_access_token({"id": str(user["_id"])})

        return {
            "success": True,
            "message": "OTP verified successfully",
            "access_token": access_token,
            "token_type": "bearer",
        }

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}",
        )


@vendor_auth_router.post("/complete-profile")
async def complete_vendor_profile(
    business_profile: BusinessProfileSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        # Check if user is verified
        current_user = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"_id": user.get("_id")}
        )

        if not current_user.get("is_verified"):
            raise HTTPException(
                status_code=403,
                detail={"success": False, "message": "User not verified"},
            )

        # Prepare business profile data
        business_data = jsonable_encoder(business_profile)

        # Update user profile
        result = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].update_one(
            {"_id": user.get("_id")},
            {
                "$set": {
                    **business_data,
                    "updated_at": datetime.now(),
                    "profile_completed": True,
                }
            },
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "message": "Profile could not be updated"},
            )

        return {"success": True, "message": "Vendor profile completed successfully"}

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Unexpected error: {str(e)}"},
        )


@vendor_auth_router.post("/login")
async def vendor_login(login_data: LoginSchema, db=Depends(get_database)):
    try:
        # Find user by email
        user = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"email": login_data.email}
        )

        if not user:
            return HTTPException(
                status_code=401,
                detail={"success": False, "message": "Invalid credentials"},
            )

        # Verify password
        if not verify_password(login_data.password, user["password"]):
            return HTTPException(
                status_code=401,
                detail={"success": False, "message": "Invalid credentials"},
            )

        # Create access token
        access_token = create_access_token({"id": user["_id"]})

        return {
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "data": {key: value for key, value in user.items() if key != "password"},
        }

    except PyMongoError as e:
        return HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Unexpected error: {str(e)}"},
        )


@vendor_auth_router.get("/profile")
async def get_vendor_profile(
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        # Fetch the vendor's profile from the database
        vendor_profile = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"_id": user.get("_id")}
        )

        if not vendor_profile:
            raise HTTPException(
                status_code=404,
                detail={"success": False, "message": "Vendor profile not found"},
            )

        # Return the profile data
        return {
            "success": True,
            "message": "Profile retrieved successfully",
            "data": VendorProfile(**vendor_profile).dict(by_alias=True),
        }

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Unexpected error: {str(e)}"},
        )
