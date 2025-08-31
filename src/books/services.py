from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import desc, select
from datetime import datetime

from src.db.models import Book
from .schemas import BookCreateModel


class BookService:
    @staticmethod
    async def create_book(book_data: BookCreateModel, user_id: int, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.published = datetime.strptime(book_data_dict["published"], "%Y-%m-%d").date()
        new_book.user_id = user_id
        session.add(new_book)
        await session.commit()
        return new_book

    @staticmethod
    async def get_all_books(session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    @staticmethod
    async def get_book(book_id: int, session: AsyncSession):
        statement = select(Book).where(Book.id == book_id)
        result = await session.exec(statement)
        return result.first()

    @staticmethod
    async def get_user_books(user_id: int, session: AsyncSession):
        statement = (select(Book).where(Book.user_id == user_id).order_by(desc(Book.created_at)))
        result = await session.exec(statement)
        return result.all()
