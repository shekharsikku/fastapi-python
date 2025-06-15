from datetime import datetime, timezone, timedelta
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from typing import Literal
import logging
import uuid

from src.config import Config


def get_timestamp():
    return datetime.now(timezone.utc)


def generate_uuid():
    return str(uuid.uuid4())


passwd_context = CryptContext(schemes=["bcrypt"])


def generate_passwd_hash(password: str) -> str:
    return passwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)


def encode_jwt_token(user_data: dict, token_type: Literal["access", "refresh"]):
    expiration = Config.ACCESS_TOKEN_EXPIRY if token_type == "access" else Config.REFRESH_TOKEN_EXPIRY
    payload = {}

    payload["user"] = user_data
    payload["type"] = token_type
    payload["jti"] = generate_uuid()
    payload["iat"] = get_timestamp()
    payload["exp"] = get_timestamp() + timedelta(seconds=expiration)

    encoded_token = jwt.encode(claims=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return encoded_token


def decode_jwt_token(jwt_token: str):
    try:
        decoded_token = jwt.decode(
            token=jwt_token, 
            key=Config.JWT_SECRET, 
            algorithms=Config.JWT_ALGORITHM, 
            options={"verify_exp": True}
        )
        return decoded_token
    except ExpiredSignatureError:
        logging.warning("Token has expired.")
        return None
    except JWTError as e:
        logging.exception("Token decoding error.")
        return None


serializer = URLSafeTimedSerializer(secret_key=Config.JWT_SECRET, salt="email-configuration")


def create_url_safe_token(data: dict):
    return serializer.dumps(data)


def decode_url_safe_token(token:str):
    try:
        return serializer.loads(token)
    except Exception as e:
        logging.error(str(e))
        return None        
    