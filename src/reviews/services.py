from fastapi import status
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.lib.response import ErrorResponse
from src.auth.services import UserService
from src.books.services import BookService
from src.db.models import Review

from .schemas import ReviewCreateModel


book_service = BookService()
user_service = UserService()


class ReviewService:
    @staticmethod
    async def add_review_to_book(book_id: int, user_id: int, review_data: ReviewCreateModel, session: AsyncSession):
        current_book = await book_service.get_book(book_id, session)

        if not current_book:
            raise ErrorResponse(status=status.HTTP_404_NOT_FOUND, message="Book not found!")
        current_user = await user_service.get_user_by_id(user_id, session)

        if not current_user:
            raise ErrorResponse(status=status.HTTP_404_NOT_FOUND, message="User not found!")

        review_data_dict = review_data.model_dump()
        review_data_dict["user_id"] = current_user.id
        review_data_dict["book_id"] = current_book.id

        new_review = Review(**review_data_dict, book=current_book, user=current_user)
        session.add(new_review)
        await session.commit()

        return new_review
