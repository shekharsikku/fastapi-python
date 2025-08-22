from fastapi import Depends, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Literal

from src.lib.response import ErrorResponse
from src.lib.utils import decode_jwt_token
from src.db.redis import redis_set_json, redis_get_json, redis_get_string
from src.db.main import get_session
from src.auth.services import UserService
from src.auth.schemas import UserModel


user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, token_type: Literal["access", "refresh"], auto_error: bool = True):
        self.token_type = token_type
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        auth_info = await super().__call__(request)
        auth_token = auth_info.credentials
        token_data = decode_jwt_token(auth_token)

        if token_data is None:
            if self.auto_error:
                raise ErrorResponse(status=status.HTTP_401_UNAUTHORIZED, message="Token is invalid or expired!")
            return None

        if self.token_type and self.token_type != token_data["type"]:
            if self.auto_error:
                raise ErrorResponse(status=status.HTTP_401_UNAUTHORIZED, message=f"Please, provide a valid {self.token_type} token!")
            return None
        
        if self.token_type == "refresh":
            stored_token = await redis_get_string(f"refresh:{token_data["uid"]}")

            if stored_token is None or stored_token != auth_token:
                raise ErrorResponse(status=status.HTTP_401_UNAUTHORIZED, message="Refresh token is invalid!")

        return token_data
        

access_token_bearer = TokenBearer(token_type="access")
refresh_token_bearer = TokenBearer(token_type="refresh")


async def get_current_user(token_data: dict = Depends(access_token_bearer), session: AsyncSession = Depends(get_session)):
    cache_data = await redis_get_json(f"user:{token_data["uid"]}")

    if cache_data is not None:
        return cache_data
    
    query_data = await user_service.get_user_by_id(token_data["uid"], session)
    user_data = UserModel.model_validate(query_data, from_attributes=True).model_dump(mode="json")
    user_data_result = await redis_set_json(f"user:{token_data["uid"]}", user_data)

    return user_data if user_data_result else None
