from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone

from src.lib.response import SuccessResponse, ErrorResponse
from src.lib.utils import verify_password, encode_jwt_token, get_timestamp
from src.lib.dependencies import get_current_user, refresh_token_bearer
from src.db.redis import redis_set_json, redis_set_string
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

    user_data = UserModel.model_validate(user_exists, from_attributes=True).model_dump(mode="json")
    user_data_result = await redis_set_json(f"user:{user_exists.id}", user_data)

    if not user_data_result:
        raise ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unable to signin!")

    access_token = encode_jwt_token(user_id=user_exists.id, token_type="access")
    res_data = {"user": user_data, "token": {"access": access_token}}

    if not user_exists.setup:
        return SuccessResponse(status=status.HTTP_200_OK, message="Please, update your profile!", data=res_data)
    
    refresh_token = encode_jwt_token(user_id=user_exists.id, token_type="refresh")
    refresh_token_result = await redis_set_string(f"refresh:{user_exists.id}", refresh_token, 86400)

    if not refresh_token_result:
        raise ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unable to signin!")

    res_data["token"]["refresh"] = refresh_token

    return SuccessResponse(status=status.HTTP_200_OK, message="Signin successfully!", data=res_data)


@auth_router.get("/me")
async def get_user_info(user_data=Depends(get_current_user)):
    if user_data is not None:
        return SuccessResponse(status=status.HTTP_200_OK, message="User information!", data=user_data)
    raise ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Something went wrong!")


@auth_router.get("/refresh-token")
async def get_new_access_token(token_data: dict = Depends(refresh_token_bearer), session: AsyncSession = Depends(get_session)):
    if datetime.fromtimestamp(token_data["exp"], timezone.utc) > get_timestamp():
        current_user_id = token_data["uid"]

        query_data = await user_service.get_user_by_id(current_user_id, session)
        user_data = UserModel.model_validate(query_data, from_attributes=True).model_dump(mode="json")
        user_data_result = await redis_set_json(f"user:{current_user_id}", user_data)

        access_token = encode_jwt_token(user_id=current_user_id, token_type="access")
        refresh_token = encode_jwt_token(user_id=current_user_id, token_type="refresh")
        refresh_token_result = await redis_set_string(f"refresh:{current_user_id}", refresh_token, 86400)

        if not refresh_token_result or not user_data_result:
            raise ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unable to refresh!")

        res_data = {"user": user_data, "token": {"access": access_token, "refresh": refresh_token}}
        return SuccessResponse(status=status.HTTP_200_OK, message="New tokens issued successfully!", data=res_data)
    
    raise ErrorResponse(status=status.HTTP_401_UNAUTHORIZED, message="Refresh token is expired!")
