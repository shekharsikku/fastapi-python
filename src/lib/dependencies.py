from fastapi import Depends, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from src.lib.response import error_response
from src.lib.utils import decode_jwt_token
from src.db.main import get_session
from src.auth.services import UserService


user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        info = await super().__call__(request)

        token = info.credentials
        data = decode_jwt_token(token)

        if data is None:
            return error_response(status.HTTP_401_UNAUTHORIZED, "Token is invalid or expired!")

        self.verify_token_data(data)
        return data

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please, override this method in child classes!")
    

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["type"] == "access":
            return error_response(status.HTTP_401_UNAUTHORIZED, "Please, provide a valid access token!")
        return None


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["type"] == "refresh":
            return error_response(status.HTTP_401_UNAUTHORIZED, "Please, provide a valid refresh token!")
        return None


access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()


async def get_current_user(details: dict = Depends(access_token_bearer), session: AsyncSession = Depends(get_session)):
    return await user_service.get_user_by_id(details["uid"], session)
