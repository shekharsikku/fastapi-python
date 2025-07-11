from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.lib.response import success_response, error_response
from src.db.main import get_session


from .schemas import UserCreateModel
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

