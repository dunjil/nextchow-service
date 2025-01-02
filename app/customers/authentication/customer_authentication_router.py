from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import PyMongoError

from app.customers.schemas import LoginSchema, OTPVerification, SignUpSchema
from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.oauth_service import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

customer_auth_router = APIRouter(prefix="/customer", tags=["Customer Authentication"])


@customer_auth_router.post("/signup")
async def customer_signup(signup_data: SignUpSchema, db=Depends(get_database)):
    try:
        # Check if user already exists
        existing_user = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_USER].find_one(
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
        user_data = signup_data.dict()
        user_data["password"] = hashed_password

        # Generate OTP
        # otp = generate_otp()
        otp = "123456"  # For testing, replace with actual OTP generation
        user_data["otp"] = get_password_hash(otp)
        user_data["otp_created_at"] = datetime.now()

        # Insert user with OTP
        result = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_USER].insert_one(user_data)

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
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Unexpected error: {str(e)}"},
        )


@customer_auth_router.post("/verify-otp")
async def verify_customer_otp(
    otp_verification: OTPVerification, db=Depends(get_database)
):
    try:
        # Find user by email
        user = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_USER].find_one(
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
                detail={"success": False, "message": "No OTP exists for this user"},
            )

        # Check OTP expiration (15 minutes)
        if (datetime.now() - otp_created_at).total_seconds() > 900:
            raise HTTPException(
                status_code=400, detail={"success": False, "message": "OTP has expired"}
            )

        # Verify OTP
        if not verify_password(otp_verification.otp, otp_hash):
            raise HTTPException(
                status_code=400, detail={"success": False, "message": "Invalid OTP"}
            )

        # Mark user as verified
        await db[NEXTCHOW_COLLECTIONS.CUSTOMER_USER].update_one(
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
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Unexpected error: {str(e)}"},
        )


@customer_auth_router.post("/login")
async def customer_login(login_data: LoginSchema, db=Depends(get_database)):
    try:
        # Find user by email
        user = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_USER].find_one(
            {"email": login_data.email}
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail={"success": False, "message": "Invalid credentials"},
            )

        # Verify password
        if not verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=401,
                detail={"success": False, "message": "Invalid credentials"},
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
            detail={"success": False, "message": f"Database error: {str(e)}"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"success": False, "message": f"Unexpected error: {str(e)}"},
        )


@customer_auth_router.post("/update-profile")
async def update_customer_profile(
    profile_data: SignUpSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        # Check if user exists
        current_user = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_USER].find_one(
            {"_id": user.get("_id")}
        )

        if not current_user:
            raise HTTPException(
                status_code=404, detail={"success": False, "message": "User not found"}
            )

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
        result = await db[NEXTCHOW_COLLECTIONS.CUSTOMER_USER].update_one(
            {"_id": user.get("_id")}, {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "message": "Profile could not be updated"},
            )

        return {"success": True, "message": "Customer profile updated successfully"}

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
