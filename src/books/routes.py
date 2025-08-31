from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from src.books.schemas import BookModel, BookCreateModel
from src.books.services import BookService
from src.db.main import get_session
from src.lib.response import SuccessResponse, ErrorResponse
from src.lib.dependencies import access_token_bearer


book_router = APIRouter()
book_service = BookService()


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookModel)
async def create_a_book(book_data: BookCreateModel, token_data: dict = Depends(access_token_bearer), session: AsyncSession = Depends(get_session)):
    return await book_service.create_book(book_data, token_data["uid"], session)


@book_router.get("/", response_model=List[BookModel])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    return await book_service.get_all_books(session)


@book_router.get("/{book_id}", response_model=BookModel)
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)):
    current_book = await book_service.get_book(book_id, session)
    if current_book:
        return current_book
    else:
        raise ErrorResponse(status=status.HTTP_404_NOT_FOUND, message="Book not found!")


@book_router.get("/user/{user_id}", response_model=List[BookModel])
async def get_user_books(user_id: int, session: AsyncSession = Depends(get_session)):
    return await book_service.get_user_books(user_id, session)
