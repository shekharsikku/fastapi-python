from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone

from src.lib.response import SuccessResponse, ErrorResponse
from src.lib.utils import verify_password, encode_jwt_token, get_timestamp, has_empty_field, generate_passwd_hash
from src.lib.dependencies import get_current_user, refresh_token_bearer, access_token_bearer
from src.db.redis import redis_client, redis_set_json, redis_set_string
from src.db.main import get_session
from src.config import Config

from .schemas import UserSignupModel, UserSigninModel, UserModel, UserUpdateModel, ChangePasswordModel, UserBooksReviewsModel
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

    access_token = encode_jwt_token(user_id=user_exists.id, token_type="access")
    refresh_token = encode_jwt_token(user_id=user_exists.id, token_type="refresh")
    refresh_token_result = await redis_set_string(f"refresh:{user_exists.id}", refresh_token, Config.REFRESH_EXPIRY)

    if not user_data_result or not refresh_token_result:
        raise ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unable to signin!")

    res_data = {"user": user_data, "token": {"access": access_token, "refresh": refresh_token}}

    if not user_exists.setup:
        del res_data["token"]["refresh"]
        return SuccessResponse(status=status.HTTP_200_OK, message="Please, update your profile!", data=res_data)

    return SuccessResponse(status=status.HTTP_200_OK, message="Signin successfully!", data=res_data)


@auth_router.get("/user-info")
async def get_user_info(user_data=Depends(get_current_user)):
    if user_data is not None:
        return SuccessResponse(status=status.HTTP_200_OK, message="User information!", data=user_data)
    raise ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Something went wrong!")


@auth_router.get("/all-info")
async def get_books_and_reviews(token_data: dict = Depends(access_token_bearer), session: AsyncSession = Depends(get_session)):
    user_data = await user_service.get_user_books_reviews(token_data["uid"], session)
    data = UserBooksReviewsModel.model_validate(user_data, from_attributes=True).model_dump(mode="json")
    return SuccessResponse(status=status.HTTP_200_OK, message="User information fetched!", data=data)


@auth_router.get("/refresh-token")
async def get_new_tokens(token_data: dict = Depends(refresh_token_bearer), session: AsyncSession = Depends(get_session)):
    if datetime.fromtimestamp(token_data["exp"], timezone.utc) > get_timestamp():
        current_user_id = token_data["uid"]

        query_data = await user_service.get_user_by_id(current_user_id, session)
        user_data = UserModel.model_validate(query_data, from_attributes=True).model_dump(mode="json")
        user_data_result = await redis_set_json(f"user:{current_user_id}", user_data)

        access_token = encode_jwt_token(user_id=current_user_id, token_type="access")
        refresh_token = encode_jwt_token(user_id=current_user_id, token_type="refresh")
        refresh_token_result = await redis_set_string(f"refresh:{current_user_id}", refresh_token, Config.REFRESH_EXPIRY)

        if not user_data_result or not refresh_token_result:
            raise ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unable to refresh!")

        res_data = {"user": user_data, "token": {"access": access_token, "refresh": refresh_token}}
        return SuccessResponse(status=status.HTTP_200_OK, message="New tokens issued successfully!", data=res_data)
    
    raise ErrorResponse(status=status.HTTP_401_UNAUTHORIZED, message="Refresh token has expired!")


@auth_router.get("/sign-out")
async def signout_user(token_data: dict = Depends(access_token_bearer)):
    current_user_id = token_data["uid"]

    await redis_client.delete(f"user:{current_user_id}")
    await redis_client.delete(f"refresh:{current_user_id}")

    return SuccessResponse(status=status.HTTP_200_OK, message="Signout successfully")


@auth_router.patch("/update-profile")
async def update_user_profile(update_data: UserUpdateModel, current_user=Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_data = update_data.model_dump_filtered()

    if user_data["username"] != current_user["username"]:
        user_exists = await user_service.user_username_exists(update_data.username, session)

        if user_exists:
            raise ErrorResponse(status=status.HTTP_409_CONFLICT, message="Username already exists!")

    user_data["setup"] = not has_empty_field(user_data)

    updated_user = await user_service.update_user(current_user["id"], user_data, session)
    updated_data = UserModel.model_validate(updated_user, from_attributes=True).model_dump(mode="json")
    user_data_result = await redis_set_json(f"user:{current_user["id"]}", updated_data)

    if not user_data_result:
        raise ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unable to update!")
    
    return SuccessResponse(status=status.HTTP_200_OK, message="Profile updated successfully!", data=updated_data)


@auth_router.patch("/change-password")
async def change_user_password(passwords: ChangePasswordModel, token_data=Depends(access_token_bearer), session: AsyncSession = Depends(get_session)):
    if passwords.old_password == passwords.new_password:
        raise ErrorResponse(status=status.HTTP_400_BAD_REQUEST, message="Please, choose a different password!")
    
    query_data = await user_service.get_user_by_id(token_data["uid"], session)

    if not query_data:
        raise ErrorResponse(status=status.HTTP_401_UNAUTHORIZED, message="Invalid authorization!")

    if not verify_password(passwords.old_password, query_data.password):
        raise ErrorResponse(status=status.HTTP_401_UNAUTHORIZED, message="Incorrect old password!")

    query_data.password = generate_passwd_hash(passwords.new_password)

    await session.commit()
    await session.refresh(query_data)

    user_data = UserModel.model_validate(query_data, from_attributes=True).model_dump(mode="json")
    user_data_result = await redis_set_json(f"user:{token_data["uid"]}", user_data)

    if not user_data_result:
        raise ErrorResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Unable to proceed!")
    
    return SuccessResponse(status=status.HTTP_200_OK, message="Password changed successfully!", data=user_data)
    