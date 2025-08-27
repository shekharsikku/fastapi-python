from datetime import datetime, timezone, timedelta
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from typing import Literal
import logging
import random
import string
import threading
import time
import uuid

from src.config import Config


# Constants
EPOCH = 1314220021721  # Custom epoch (same as in your SQL)
SHARD_ID = 1           # Can be set differently per server
SEQUENCE_MASK = 1023   # 10 bits = 1024 values max

# Globals
last_timestamp = -1
sequence = 0
lock = threading.Lock()


def current_millis():
    return int(time.time() * 1000)


def wait_next_millis(last_ts):
    ts = current_millis()
    while ts <= last_ts:
        ts = current_millis()
    return ts


def generate_id():
    """Generate unique id according to current time stamp."""
    global last_timestamp, sequence

    with lock:
        now_ms = current_millis()
        
        if now_ms == last_timestamp:
            sequence = (sequence + 1) & SEQUENCE_MASK
            if sequence == 0:
                now_ms = wait_next_millis(last_timestamp)
        else:
            sequence = 0

        last_timestamp = now_ms

        id_val = ((now_ms - EPOCH) << 23) | (SHARD_ID << 10) | sequence
        return id_val


def generate_suffix(length: int = 6) -> str:
    """Generate random suffix for uniqueness."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_timestamp():
    """Get current timestamp with utc timezone."""
    return datetime.now(timezone.utc)


def generate_uuid():
    """Generate unique uuid by using uuid v4.."""
    return str(uuid.uuid4())


passwd_context = CryptContext(schemes=["bcrypt"])


def generate_passwd_hash(password: str) -> str:
    """Generate hash from password."""
    return passwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify password by hash."""
    return passwd_context.verify(password, hashed)


def encode_jwt_token(user_id: int, token_type: Literal["access", "refresh"]):
    """Encode JWT token."""
    expiration = Config.ACCESS_EXPIRY if token_type == "access" else Config.REFRESH_EXPIRY
    payload = {"type": token_type, "uid": user_id, "iat": get_timestamp(), "exp": get_timestamp() + timedelta(seconds=expiration)}
    return jwt.encode(claims=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)


def decode_jwt_token(jwt_token: str):
    """Decode JWT token."""
    try:
        decoded_token = jwt.decode(
            token=jwt_token, 
            key=Config.JWT_SECRET, 
            algorithms=Config.JWT_ALGORITHM, 
            options={"verify_exp": True}
        )
        return decoded_token
    except ExpiredSignatureError:
        logging.warning("Token has expired!")
        return None
    except JWTError as e:
        logging.exception("Token decoding error!", str(e))
        return None


serializer = URLSafeTimedSerializer(secret_key=Config.JWT_SECRET, salt="email-configuration")


def create_url_safe_token(data: dict):
    """Create URL safe token."""
    return serializer.dumps(data)


def decode_url_safe_token(token: str):
    """Decode URL safe token."""
    try:
        return serializer.loads(token)
    except Exception as e:
        logging.error(str(e))
        return None        
    

def has_empty_field(fields: dict) -> bool:
    return any(value in ("", None) for value in fields.values())
