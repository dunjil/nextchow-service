import os

import requests
from dotenv import load_dotenv

load_dotenv()

"""We use Mailer Lite to maintain a subscription list for our users"""


""" We use Mailer send to send transactional emails """


class Envs:
    MAILER_SEND_TOKEN = os.getenv("MAILER_SEND_TOKEN")
    MAILER_LITE_TOKEN = os.getenv("MAILER_LITE_TOKEN")
    WELCOME_TEMPLATE_ID = os.getenv("WELCOME_TEMPLATE_ID")
    PASS_TEMPLATE_ID = os.getenv("PASS_TEMPLATE_ID")
    PASSWORD_RESET_TEMPLATE_ID = os.getenv("PASSWORD_RESET_TEMPLATE_ID")


async def send_welcome_email(reciever_email: str, reciever_firstname: str):
    url = "https://api.mailersend.com/v1/email"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {Envs.MAILER_SEND_TOKEN}",
    }

    data = {
        "from": {"email": "info@databoard.ai"},
        "to": [{"email": reciever_email}],
        "personalization": [
            {"email": reciever_email, "data": {"name": reciever_firstname}}
        ],
        "subject": "Welcome to Clocker",
        "template_id": Envs.WELCOME_TEMPLATE_ID,
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201, 202, 204]:
        print("Email sent successfully!")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False


async def send_pass_email_to_users(
    reciever_email: str,
    host: str,
    event_name: str,
    claim_url: str,
    conjunction: str,
    type: str,
    ticket_name: str,
    ticket_type: str,
    sender: str,
):
    url = "https://api.mailersend.com/v1/email"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {Envs.MAILER_SEND_TOKEN}",
    }

    data = {
        "from": {"email": "info@databoard.ai"},
        "to": [{"email": reciever_email}],
        "variables": [
            {
                "email": reciever_email,
                "substitutions": [
                    {"var": "host", "value": host},
                    {"var": "type", "value": type},
                    {"var": "sender", "value": sender},
                    {"var": "event_name", "value": event_name},
                    {"var": "conjunction", "value": conjunction},
                    {"var": "ticket_name", "value": ticket_name},
                    {"var": "ticket_type", "value": ticket_type},
                    {"var": "claim_url", "value": claim_url},
                ],
            }
        ],
        "subject": "You got a free pass",
        "personalization": [{"email": reciever_email, "data": {"type": ""}}],
        "template_id": Envs.PASS_TEMPLATE_ID,
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201, 202, 204]:
        print("Email sent successfully!")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False


async def send_password_reset_mail(
    reciever_email: str, reciever_firstname: str, otp: str
):
    url = "https://api.mailersend.com/v1/email"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {Envs.MAILER_SEND_TOKEN}",
    }

    data = {
        "from": {"email": "info@databoard.ai"},
        "to": [{"email": reciever_email}],
        "variables": [
            {
                "email": reciever_email,
                "substitutions": [
                    {"var": "otp", "value": otp},
                    {"var": "name", "value": reciever_firstname},
                ],
            }
        ],
        "subject": "Password Reset",
        "template_id": Envs.PASSWORD_RESET_TEMPLATE_ID,
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201, 202, 204]:
        print("Email sent successfully!")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False


async def send_reg_otp_mail(reciever_email: str, reciever_name: str, otp: str):
    url = "https://api.mailersend.com/v1/email"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {Envs.MAILER_SEND_TOKEN}",
    }

    data = {
        "from": {"email": "info@databoard.ai"},
        "to": [{"email": reciever_email}],
        "variables": [
            {
                "email": reciever_email,
                "substitutions": [
                    {"var": "otp", "value": otp},
                    {"var": "name", "value": reciever_name},
                ],
            }
        ],
        "subject": "Welcome to Clocker",
        "template_id": "3vz9dlevy5q4kj50",
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201, 202, 204]:
        print("Email sent successfully!")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False

async def send_password_reset_otp(reciever_email: str, reciever_name: str, otp: str):
    url = "https://api.mailersend.com/v1/email"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {Envs.MAILER_SEND_TOKEN}",
    }

    data = {
        "from": {"email": "info@databoard.ai"},
        "to": [{"email": reciever_email}],
        "variables": [
            {
                "email": reciever_email,
                "substitutions": [
                    {"var": "otp", "value": otp},
                    {"var": "name", "value": reciever_name},
                ],
            }
        ],
        "subject": "Welcome to Clocker",
        "template_id": "3vz9dlevy5q4kj50",
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201, 202, 204]:
        print("Email sent successfully!")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False


async def add_user_to_default_mail_list(
    user_firstname: str, user_lastname: str, user_email: str
):
    url = "https://connect.mailerlite.com/api/subscribers"

    headers = {
        "Authorization": f"Bearer {Envs.MAILER_LITE_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {
        "email": user_email,
        "fields": {"name": user_firstname, "last_name": user_lastname},
        "groups": [
            "122156676408149459",
        ],
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        print("New subscriber added successfully:")

        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")

        return False
