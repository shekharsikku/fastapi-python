import redis.asyncio as aioredis
import json

from src.config import Config


redis_client = aioredis.from_url(Config.REDIS_URL, decode_responses=True)


async def redis_set_json(key: str, value: dict, expire = 3600):
    data = json.dumps(value)
    return await redis_client.set(key, data, ex=expire)


async def redis_get_json(key: str) -> dict | None:
    data = await redis_client.get(key)
    return json.loads(data) if data else None


async def redis_set_string(key: str, value: str, expire = 3600):
    return await redis_client.set(key, value, ex=expire)


async def redis_get_string(key: str) -> str | None:
    data = await redis_client.get(key)
    return data if data else None
