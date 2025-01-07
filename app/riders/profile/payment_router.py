import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import PyMongoError

from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database
from app.general.utils.oauth_service import get_current_user
from app.riders.schemas import BankAccountSchema, ResolveBankAccountSchema

vendor_payment_router = APIRouter(prefix="/rider", tags=["Rider Payment Management"])
load_dotenv()


@vendor_payment_router.post("/bank-account")
async def add_bank_account(
    bank_data: BankAccountSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        # Check if bank account already exists for the user
        existing_account = await db[NEXTCHOW_COLLECTIONS.VENDOR_BANK_ACCOUNT].find_one(
            {"user_id": str(user["_id"])}
        )
        if existing_account:
            return {
                "success": False,
                "message": "Bank account already exists for this user",
            }

        # Insert new bank account
        bank_account = {
            "user_id": str(user["_id"]),
            "account_name": bank_data.account_name,
            "bank_code": bank_data.bank_code,
            "bank_name": bank_data.bank_name,
            "account_number": bank_data.account_number,
            "created_at": datetime.now(),
        }
        await db[NEXTCHOW_COLLECTIONS.VENDOR_BANK_ACCOUNT].insert_one(bank_account)

        return {"success": True, "message": "Bank account added successfully"}


    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e

@vendor_payment_router.put("/bank-account")
async def update_bank_account(
    bank_data: BankAccountSchema,
    user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    try:
        # Check if the bank account exists
        existing_account = await db[NEXTCHOW_COLLECTIONS.VENDOR_BANK_ACCOUNT].find_one(
            {"user_id": str(user["_id"])}
        )
        if not existing_account:
            return {
                "success": False,
                "message": "Bank account not found for this user",
            }

        # Update bank account details
        await db[NEXTCHOW_COLLECTIONS.VENDOR_BANK_ACCOUNT].update_one(
            {"user_id": str(user["_id"])},
            {
                "$set": {
                    "account_name": bank_data.account_name,
                    "bank_code": bank_data.bank_code,
                    "bank_name": bank_data.bank_name,
                    "account_number": bank_data.account_number,
                    "updated_at": datetime.now(),
                }
            },
        )

        return {"success": True, "message": "Bank account updated successfully"}


    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e

@vendor_payment_router.get("/bank-account")
async def get_bank_account_details(
    user: dict = Depends(get_current_user), db=Depends(get_database)
):
    try:
        # Fetch bank account details for the user
        bank_account = await db[NEXTCHOW_COLLECTIONS.VENDOR_BANK_ACCOUNT].find_one(
            {"user_id": str(user["_id"])}
        )

        if not bank_account:
            return {
                "success": False,
                "message": "Bank account details not found for this user",
            }

        # Return the bank account details
        return {
            "success": True,
            "data": {
                "account_name": bank_account["account_name"],
                "bank_code": bank_account["bank_code"],
                "bank_name": bank_account["bank_name"],
                "account_number": bank_account["account_number"],
            },
        }


    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise e

@vendor_payment_router.get("/get_all_nigerian_banks")
async def get_all_nigerian_banks(
    current_user: dict = Depends(get_current_user),
):
    try:
        url = "https://api.paystack.co/bank"
        response = requests.get(url)

        if response.status_code == 200:
            all_banks = response.json()
            return {
                "status_code": status.HTTP_200_OK,
                "status": "success",
                "message": "Successfully deleted payment information",
                "data": all_banks.get("data"),
            }

        else:
            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "status": "error",
                    "message": " Something when wrong",
                    "data": f"{response.json()}",
                },
            )

    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Something went wrong {e}",
                "data": "",
            },
        )


@vendor_payment_router.post("/resolve_nigerian_account")
async def resolve_nigerian_account(
    bank_data: ResolveBankAccountSchema,
):
    try:
        url = f"https://api.paystack.co/bank/resolve?account_number={bank_data.account_number}&bank_code={bank_data.bank_code}"
        headers = {
            "Authorization": f"Bearer {os.getenv('PAYMENT_SECRET_KEY')}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            bank_details = response.json()

            return {
                "status_code": status.HTTP_200_OK,
                "status": "success",
                "message": "Account details retrieved successfully",
                "data": bank_details.get("data"),
            }

        else:
            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "status": "error",
                    "message": " Something when wrong",
                    "data": f"{response.json()}",
                },
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Something went wrong {e}",
                "data": "",
            },
        )
