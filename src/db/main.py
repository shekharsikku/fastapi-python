from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, create_engine, text
from typing import Any

from src.config import Config


async_engine = AsyncEngine(create_engine(url=Config.DATABASE_URL, echo=True))


async def test_db() -> None:
    async with async_engine.begin() as connection:
        statement = text("SELECT 'hello';")
        result = await connection.execute(statement)
        print("Connection Result:", result.all())


async def init_db() -> None:
    async with async_engine.begin() as connection:
        # from .models import User, Book, Review
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session() -> Any:
    current_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with current_session() as session:
        yield session
