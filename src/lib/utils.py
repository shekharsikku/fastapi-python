from datetime import datetime, timezone, timedelta
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
import logging
import uuid
import jwt

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


def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=Config.ACCESS_TOKEN_EXPIRY))
    payload["jti"] = str(uuid.uuid4())

    payload["refresh"] = refresh

    return jwt.encode(payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
    
    except jwt.PyJWTError as e:
        logging.exception(e)
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
    