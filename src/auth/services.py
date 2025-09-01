from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from fastapi import status

from src.lib.response import ErrorResponse
from src.lib.utils import generate_passwd_hash
from src.db.models import User
from .schemas import UserSignupModel


class UserService:
    @staticmethod
    async def get_user_by_id(id: int, session: AsyncSession):
        statement = select(User).where(User.id == id)
        result = await session.exec(statement)
        return result.first()
    
    @staticmethod
    async def get_user_by_email(email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def get_user_by_username(username: str, session: AsyncSession):
        statement = select(User).where(User.username == username)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def user_email_exists(email, session: AsyncSession):
        user = await UserService.get_user_by_email(email, session)
        return user is not None

    @staticmethod
    async def user_username_exists(username, session: AsyncSession):
        user = await UserService.get_user_by_username(username, session)
        return user is not None

    @staticmethod
    async def create_user(user_data: UserSignupModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password = generate_passwd_hash(user_data_dict["password"])
        session.add(new_user)
        await session.commit()
        return new_user

    @staticmethod
    async def update_user(user_id: int, user_data: dict, session: AsyncSession):
        statement = select(User).where(User.id == user_id)
        result = await session.exec(statement)
        user = result.first()

        if not user:
            raise ErrorResponse(status=status.HTTP_404_NOT_FOUND, message="User not found!")

        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_user_books_reviews(user_id: int, session: AsyncSession):
        statement = select(User).options(
            selectinload(User.books), 
            selectinload(User.reviews)
        ).where(User.id == user_id)

        return await session.scalar(statement)
