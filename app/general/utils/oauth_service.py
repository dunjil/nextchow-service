import os
from datetime import datetime, timedelta
from typing import Dict

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.general.utils.database import NEXTCHOW_COLLECTIONS, get_database

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRY_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    id: str


def create_access_token(data: Dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=100)
    to_encode.update({"exp": expire})
    jwt_token = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token


def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)

        id: str = payload.get("id")
        if not id:
            raise credential_exception
        token_data = TokenData(id=id)
        return token_data
    except JWTError:
        raise credential_exception


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db=Depends(get_database)
):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )

    credentail_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "status": "token_expired",
            "message": "Your session is expired",
            "data": "",
        },
    )
    if token.startswith("Bearer "):
        token = token[len("Bearer ") :]

    current_user_id = verify_access_token(token, credentail_exception).id

    current_user = await db[NEXTCHOW_COLLECTIONS.VENDOR_USER].find_one(
        {"_id": current_user_id}
    )
    return current_user
