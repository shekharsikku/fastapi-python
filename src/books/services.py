from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import desc, select

from src.db.models import Book
from .schemas import BookCreateModel, BookUpdateModel


class BookService:
    @staticmethod
    async def create_book(book_data: BookCreateModel, user_id: int, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
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

    @staticmethod
    async def update_book(book_id: int, update_data: BookUpdateModel, session: AsyncSession):
        book_to_update = await BookService.get_book(book_id, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump(exclude_unset=True)
            
            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)
            
            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update
        else:
            return None

    @staticmethod
    async def delete_book(book_id: int, session: AsyncSession):
        book_to_delete = await BookService.get_book(book_id, session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return True
        else:
            return False
