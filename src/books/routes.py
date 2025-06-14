from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from src.books.schemas import BookModel, BookCreateModel, BookUpdateModel
from src.books.services import BookService
from src.db.main import get_session
from src.lib.errors import BookNotFound


book_router = APIRouter()
book_service = BookService()


@book_router.get("/", response_model=List[BookModel])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    all_books = await book_service.get_all_books(session)
    return all_books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookModel)
async def create_a_book(book_data: BookCreateModel, session: AsyncSession = Depends(get_session)):
    new_book = await book_service.create_book(book_data, session)
    return new_book


@book_router.get("/{book_id}", response_model=BookModel)
async def get_book(book_id: str, session: AsyncSession = Depends(get_session)):
    current_book = await book_service.get_book(book_id, session)
    if current_book:
        return current_book
    else:
        raise BookNotFound()
    

@book_router.patch("/{book_id}", response_model=BookModel)
async def update_book(book_id: str, book_update_data: BookUpdateModel, session: AsyncSession = Depends(get_session)):
    updated_book = await book_service.update_book(book_id, book_update_data, session)

    if updated_book is None:
        raise BookNotFound()
    else:
        return updated_book


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str, session: AsyncSession = Depends(get_session),):
    book_to_delete = await book_service.delete_book(book_id, session)

    if book_to_delete is None:
        raise BookNotFound()
    else:
        return {}
