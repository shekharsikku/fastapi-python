from fastapi import Depends, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Literal

from src.lib.response import ErrorResponse
from src.lib.utils import decode_jwt_token
from src.db.main import get_session
from src.auth.services import UserService


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

        return token_data
        

access_token_bearer = TokenBearer(token_type="access")
refresh_token_bearer = TokenBearer(token_type="refresh")


async def get_current_user(token_data: dict = Depends(access_token_bearer), session: AsyncSession = Depends(get_session)):
    return await user_service.get_user_by_id(token_data["uid"], session)
