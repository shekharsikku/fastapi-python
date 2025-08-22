from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone

from src.lib.response import SuccessResponse, ErrorResponse
from src.lib.utils import verify_password, encode_jwt_token, get_timestamp
from src.lib.dependencies import get_current_user, refresh_token_bearer
from src.db.main import get_session

from .schemas import UserSignupModel, UserSigninModel, UserModel
from .services import UserService


auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def signup_user(user_data: UserSignupModel, session: AsyncSession = Depends(get_session)):
    user_exists = await user_service.user_email_exists(user_data.email, session)
    
    if user_exists:
        raise ErrorResponse(status=status.HTTP_409_CONFLICT, message="Email already exists!")

    await user_service.create_user(user_data, session)

    return SuccessResponse(status=status.HTTP_201_CREATED, message="Signup successfully!")


@auth_router.post("/sign-in")
async def signin_user(login_data: UserSigninModel, session: AsyncSession = Depends(get_session)):
    user_exists = (
        await user_service.get_user_by_email(login_data.email, session)
        if login_data.email
        else await user_service.get_user_by_username(login_data.username, session)
    )

    if not user_exists:
        raise ErrorResponse(status=status.HTTP_404_NOT_FOUND, message="User not found!")

    password_valid = verify_password(login_data.password, user_exists.password)

    if not password_valid:
        raise ErrorResponse(status=status.HTTP_401_UNAUTHORIZED, message="Invalid credentials!")

    access_token = encode_jwt_token(user_id=user_exists.id, token_type="access")
    res_data = {
        "id": user_exists.id, 
        "email": user_exists.email, 
        "setup": user_exists.setup, 
        "access_token": access_token
    }

    if not user_exists.setup:
        return SuccessResponse(status=status.HTTP_200_OK, message="Please, complete your profile!", data=res_data)
    
    refresh_token = encode_jwt_token(user_id=user_exists.id, token_type="refresh")
    res_data["refresh_token"] = refresh_token

    return SuccessResponse(status=status.HTTP_200_OK, message="Signin successfully!", data=res_data)


@auth_router.get("/me")
async def get_user_info(query_user=Depends(get_current_user)):
    user_data = UserModel.model_validate(query_user, from_attributes=True).model_dump(mode="json")
    return SuccessResponse(status=status.HTTP_200_OK, message="User information!", data=user_data)


@auth_router.get("/refresh-token")
async def get_new_access_token(token_data: dict = Depends(refresh_token_bearer)):
    if datetime.fromtimestamp(token_data["exp"], timezone.utc) > get_timestamp():
        access_token = encode_jwt_token(user_id=token_data["uid"], token_type="access")
        return SuccessResponse(status=status.HTTP_200_OK, message="Token refreshed successfully!", data=access_token)
    raise ErrorResponse(status=status.HTTP_401_UNAUTHORIZED, message="Token is invalid or expired!")
