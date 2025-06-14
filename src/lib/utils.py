from datetime import datetime, timezone
import uuid


def get_timestamp():
    return datetime.now(timezone.utc)


def generate_uuid():
    return str(uuid.uuid4())
