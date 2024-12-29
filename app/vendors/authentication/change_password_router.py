from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import PyMongoError

from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.mail_sender import send_password_reset_otp
from app.general.utils.oauth_service import (
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.vendors.schemas import (
    ChangePasswordSchema,
    OTPVerification,
    PasswordResetRequestSchema,
    PasswordResetSchema,
)

vendor_password_router = APIRouter(
    prefix="/vendor", tags=["Vendor Password Management"]
)


@vendor_password_router.post("/request-password-reset")
async def request_password_reset(
    reset_request: PasswordResetRequestSchema, db=Depends(get_database)
):
    try:
        # Find user by email
        user = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"email": reset_request.email}
        )

        if not user:
            # Deliberately vague response to prevent email enumeration
            return {
                "success": True,
                "message": "If an account exists with this email, a reset OTP will be sent",
            }

        # Generate OTP
        otp = "123456"

        # Hash OTP for secure storage
        otp_hash = get_password_hash(otp)

        # Update user with OTP and creation time
        await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].update_one(
            {"email": reset_request.email},
            {
                "$set": {
                    "password_reset_otp": otp_hash,
                    "password_reset_otp_created_at": datetime.now(),
                }
            },
        )

        # Send OTP via email
        await send_password_reset_otp(reset_request.email, otp)

        return {"success": True, "message": "Password reset OTP sent to your email"}

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


@vendor_password_router.post("/verify-password-reset-otp")
async def verify_password_reset_otp(
    otp_verification: OTPVerification, db=Depends(get_database)
):
    try:
        # Find user by email
        user = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"email": otp_verification.email}
        )

        if not user:
            raise HTTPException(
                status_code=404, detail={"success": False, "message": "User not found"}
            )

        # Check if OTP exists and is not expired
        otp_hash = user.get("password_reset_otp")
        otp_created_at = user.get("password_reset_otp_created_at")

        if not otp_hash or not otp_created_at:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "message": "No password reset OTP exists"},
            )

        # Check OTP expiration (e.g., 15 minutes)
        if (datetime.now() - otp_created_at).total_seconds() > 900:
            await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].update_one(
                {"email": otp_verification.email},
                {
                    "$unset": {
                        "password_reset_otp": 1,
                        "password_reset_otp_created_at": 1,
                    }
                },
            )
            raise HTTPException(
                status_code=400, detail={"success": False, "message": "OTP has expired"}
            )

        # Verify OTP
        if not verify_password(otp_verification.otp, otp_hash):
            raise HTTPException(
                status_code=400, detail={"success": False, "message": "Invalid OTP"}
            )

        # Mark OTP as verified
        await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].update_one(
            {"email": otp_verification.email},
            {"$set": {"password_reset_otp_verified": True}},
        )

        return {
            "success": True,
            "message": "OTP verified successfully. You can now reset your password",
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


@vendor_password_router.post("/reset-password")
async def reset_password(password_reset: PasswordResetSchema, db=Depends(get_database)):
    try:
        # Find user by email
        user = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"email": password_reset.email}
        )

        if not user:
            raise HTTPException(
                status_code=404, detail={"success": False, "message": "User not found"}
            )

        # Check if OTP was verified
        if not user.get("password_reset_otp_verified"):
            raise HTTPException(
                status_code=403,
                detail={"success": False, "message": "OTP not verified"},
            )

        # Check if new password is different from current password
        if verify_password(password_reset.new_password, user["password"]):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": "New password must be different from current password",
                },
            )

        # Hash new password
        new_password_hash = get_password_hash(password_reset.new_password)

        # Update password and clean up reset-related fields
        result = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].update_one(
            {"email": password_reset.email},
            {
                "$set": {"password": new_password_hash, "updated_at": datetime.now()},
                "$unset": {
                    "password_reset_otp": 1,
                    "password_reset_otp_created_at": 1,
                    "password_reset_otp_verified": 1,
                },
            },
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "message": "Password could not be updated"},
            )

        return {"success": True, "message": "Password reset successfully"}

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


# Optional: Change password when logged in
@vendor_password_router.post("/change-password")
async def change_password(
    password_change: ChangePasswordSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        # Find user by ID
        current_user = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
            {"_id": user.get("_id")}
        )

        # Verify current password
        if not verify_password(
            password_change.current_password, current_user["password"]
        ):
            raise HTTPException(
                status_code=400,
                detail={"success": False, "message": "Current password is incorrect"},
            )

        # Check if new password is different from current password
        if verify_password(password_change.new_password, current_user["password"]):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": "New password must be different from current password",
                },
            )

        # Hash new password
        new_password_hash = get_password_hash(password_change.new_password)

        # Update password
        result = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].update_one(
            {"_id": user.get("_id")},
            {"$set": {"password": new_password_hash, "updated_at": datetime.now()}},
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"success": False, "message": "Password could not be updated"},
            )

        return {"success": True, "message": "Password changed successfully"}

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
