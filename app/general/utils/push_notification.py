import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")


async def send_push_notification(device_token: str, title: str, body: str):
    """Send a push notification using FCM."""
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"to": device_token, "notification": {"title": title, "body": body}}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://fcm.googleapis.com/fcm/send", json=payload, headers=headers
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=500, detail="Failed to send push notification"
            )
