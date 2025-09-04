from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.lib.response import ErrorResponse, SuccessResponse
from src.lib.dependencies import access_token_bearer
from src.db.main import get_session

from src.books.schemas import BookDetailModel
from src.books.services import BookService
from .schemas import ReviewCreateModel, ReviewModel
from .services import ReviewService


review_router = APIRouter()
review_service = ReviewService()
book_service = BookService()


@review_router.post("/book/{book_id}")
async def add_review_to_books(
    book_id: int, review_data: ReviewCreateModel, token_data: dict = Depends(access_token_bearer), session: AsyncSession = Depends(get_session)
):
    new_review = await review_service.add_review_to_book(book_id, token_data["uid"], review_data, session)
    created_review = ReviewModel.model_validate(new_review, from_attributes=True).model_dump(mode="json")
    return SuccessResponse(status=status.HTTP_201_CREATED, message="Review created successfully!", data=created_review)


@review_router.get("/book/{book_id}")
async def get_book_reviews(book_id: int, session: AsyncSession = Depends(get_session), _: dict = Depends(access_token_bearer)):
    current_book = await book_service.get_book(book_id, session)
    book_data = BookDetailModel.model_validate(current_book, from_attributes=True).model_dump(mode="json")
    return SuccessResponse(status=status.HTTP_200_OK, message="Book and reviews fetched successfully!", data=book_data)
