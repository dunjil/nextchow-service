from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.errors import PyMongoError

from app.customers.schemas import LoginSchema, OTPVerification, SignUpSchema
from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.oauth_service import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

rider_auth_router = APIRouter(prefix="/rider", tags=["Rider Authentication"])


@rider_auth_router.post("/signup")
async def rider_signup(signup_data: SignUpSchema, db=Depends(get_database)):
    try:
        # Check if user already exists
        existing_user = await db[NEXTCHOW_COLLECTIONS.RIDER_USER].find_one(
            {"email": signup_data.email}
        )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

        # Hash the password
        hashed_password = get_password_hash(signup_data.password)

        # Prepare user data
        user_data = signup_data.dict()
        user_data["password"] = hashed_password

        # Generate OTP
        # otp = generate_otp()
        otp = "123456"  # For testing, replace with actual OTP generation
        user_data["otp"] = get_password_hash(otp)
        user_data["otp_created_at"] = datetime.now()
        data = jsonable_encoder(user_data)

        # Insert user with OTP
        result = await db[NEXTCHOW_COLLECTIONS.RIDER_USER].insert_one(data)

        # Send OTP via email (commented out for testing)
        # await send_reg_otp_mail(signup_data.email, otp)

        return {
            "success": True,
            "message": "Signup successful. OTP sent to your email.",
            "user_id": str(result.inserted_id),
        }

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


@rider_auth_router.post("/verify-otp")
async def verify_rider_otp(otp_verification: OTPVerification, db=Depends(get_database)):
    try:
        # Find user by email
        user = await db[NEXTCHOW_COLLECTIONS.RIDER_USER].find_one(
            {"email": otp_verification.email}
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if OTP is valid and not expired
        otp_hash = user.get("otp")
        otp_created_at = user.get("otp_created_at")

        if not otp_hash or not otp_created_at:
            raise HTTPException(
                status_code=400,
                detail="No OTP exists for this user",
            )

        # Check OTP expiration (15 minutes)
        if (datetime.now() - otp_created_at).total_seconds() > 900:
            raise HTTPException(status_code=400, detail="OTP has expired")

        # Verify OTP
        if not verify_password(otp_verification.otp, otp_hash):
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # Mark user as verified
        await db[NEXTCHOW_COLLECTIONS.RIDER_USER].update_one(
            {"email": otp_verification.email},
            {"$set": {"is_verified": True}, "$unset": {"otp": 1, "otp_created_at": 1}},
        )

        # Create access token
        access_token = create_access_token({"sub": str(user["_id"])})

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
        raise e


@rider_auth_router.post("/login")
async def rider_login(login_data: LoginSchema, db=Depends(get_database)):
    try:
        # Find user by email
        user = await db[NEXTCHOW_COLLECTIONS.RIDER_USER].find_one(
            {"email": login_data.email}
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        # Verify password
        if not verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        # Create access token
        access_token = create_access_token({"sub": str(user["_id"])})

        return {
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
        }

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


@rider_auth_router.post("/update-profile")
async def update_rider_profile(
    profile_data: SignUpSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        # Check if user exists
        current_user = await db[NEXTCHOW_COLLECTIONS.RIDER_USER].find_one(
            {"_id": user.get("_id")}
        )

        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Prepare update data
        update_data = {
            "first_name": profile_data.first_name,
            "last_name": profile_data.last_name,
            "phone": profile_data.phone,
            "location": profile_data.location.dict(),
            "address": profile_data.address,
            "updated_at": datetime.now(),
        }

        # Update user profile
        result = await db[NEXTCHOW_COLLECTIONS.RIDER_USER].update_one(
            {"_id": user.get("_id")}, {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail="Profile could not be updated",
            )

        return {"success": True, "message": "Rider profile updated successfully"}

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e


@rider_auth_router.get("/profile")
async def get_rider_profile(
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        # Fetch the rider's profile from the database
        rider_profile = await db[NEXTCHOW_COLLECTIONS.RIDER_USER].find_one(
            {"_id": user.get("_id")}
        )

        if not rider_profile:
            raise HTTPException(
                status_code=404,
                detail="Rider profile not found",
            )

        # Prepare the profile data to return
        profile_data = {
            "first_name": rider_profile.get("first_name"),
            "last_name": rider_profile.get("last_name"),
            "phone": rider_profile.get("phone"),
            "location": rider_profile.get("location"),
            "address": rider_profile.get("address"),
            "created_at": rider_profile.get("created_at"),
            "updated_at": rider_profile.get("updated_at"),
        }

        return {"success": True, "data": profile_data}

    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e
