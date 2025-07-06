import redis.asyncio as aioredis

from src.config import Config


redis_client = aioredis.from_url(Config.REDIS_URL);


async def token_to_blacklist(key: str, value: str) -> str:
    result = await redis_client.set(name=f"jti:{key}", value=value, ex=3600)
    return result


async def token_in_blacklist(key: str) -> bool:
    token = await redis_client.get(f"jti:{key}")
    return token is not None
