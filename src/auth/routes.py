from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.lib.utils import verify_password, encode_jwt_token, get_timestamp
from src.lib.response import success_response, error_response
from src.lib.dependencies import get_current_user
from src.db.main import get_session

from .schemas import UserCreateModel, UserLoginModel, UserModel
from .services import UserService


auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def signup_user(user_data: UserCreateModel, session: AsyncSession = Depends(get_session)):
    user_exists = await user_service.user_email_exists(user_data.email, session)
    
    if user_exists:
        return error_response(status.HTTP_409_CONFLICT, "Email already exists!")

    await user_service.create_user(user_data, session)

    return success_response(status.HTTP_201_CREATED, "Signup successfully!")


@auth_router.post("/sign-in")
async def signin_user(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    user_exists = (
        await user_service.get_user_by_email(login_data.email, session)
        if login_data.email
        else await user_service.get_user_by_username(login_data.username, session)
    )

    if not user_exists:
        return error_response(status.HTTP_404_NOT_FOUND, "User not found!")

    password_valid = verify_password(login_data.password, user_exists.password)

    if not password_valid:
        return error_response(status.HTTP_401_UNAUTHORIZED, "Invalid credentials!")

    access_token = encode_jwt_token(user_id=user_exists.id, token_type="access")
    res_data = {
        "id": user_exists.id, 
        "email": user_exists.email, 
        "setup": user_exists.setup, 
        "access_token": access_token
    }

    if not user_exists.setup:
        return success_response(status.HTTP_200_OK, "Please, complete your profile!", res_data)
    
    refresh_token = encode_jwt_token(user_data=user_exists.id, token_type="refresh")
    res_data["refresh_token"] = refresh_token

    return success_response(status.HTTP_200_OK, "Signin successfully!", res_data)


@auth_router.get("/me")
async def get_user_info(query_user=Depends(get_current_user)):
    user_data = UserModel.model_validate(query_user, from_attributes=True).model_dump(mode="json")
    return success_response(status.HTTP_200_OK, "User information!", user_data)
