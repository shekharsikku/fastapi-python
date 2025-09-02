from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import TypeAdapter
from typing import List

from src.books.schemas import BookModel, BookCreateModel, BookUpdateModel
from src.books.services import BookService
from src.db.main import get_session
from src.lib.response import SuccessResponse, ErrorResponse
from src.lib.dependencies import access_token_bearer


book_router = APIRouter()
book_service = BookService()
book_adapter = TypeAdapter(List[BookModel])


@book_router.post("/")
async def create_a_book(book_data: BookCreateModel, token_data: dict = Depends(access_token_bearer), session: AsyncSession = Depends(get_session)):
    current_book = await book_service.create_book(book_data, token_data["uid"], session)
    book_data = BookModel.model_validate(current_book, from_attributes=True).model_dump(mode="json")
    return SuccessResponse(status=status.HTTP_201_CREATED, message="Book created successfully!", data=book_data)


@book_router.get("/")
async def get_all_books(session: AsyncSession = Depends(get_session), _: dict = Depends(access_token_bearer)):
    all_books = await book_service.get_all_books(session)
    books_data = book_adapter.validate_python(all_books, from_attributes=True)
    books_data = book_adapter.dump_python(books_data, mode="json")
    return SuccessResponse(status=status.HTTP_200_OK, message="Books fetched successfully!", data=books_data)


@book_router.get("/{book_id}")
async def get_book(book_id: int, session: AsyncSession = Depends(get_session), _: dict = Depends(access_token_bearer)):
    current_book = await book_service.get_book(book_id, session)
    if current_book:
        book_data = BookModel.model_validate(current_book, from_attributes=True).model_dump(mode="json")
        return SuccessResponse(status=status.HTTP_200_OK, message="Book fetched successfully!", data=book_data)
    else:
        raise ErrorResponse(status=status.HTTP_404_NOT_FOUND, message="Book not found!")


@book_router.get("/user/{user_id}")
async def get_user_books(user_id: int, session: AsyncSession = Depends(get_session), _: dict = Depends(access_token_bearer)):
    all_books = await book_service.get_user_books(user_id, session)
    books_data = book_adapter.validate_python(all_books, from_attributes=True)
    books_data = book_adapter.dump_python(books_data, mode="json")
    return SuccessResponse(status=status.HTTP_200_OK, message="Books fetched successfully!", data=books_data)


@book_router.patch("/{book_id}")
async def update_book(book_id: int, update_data: BookUpdateModel, session: AsyncSession = Depends(get_session), token_data: dict = Depends(access_token_bearer)):
    updated_book = await book_service.update_book(book_id, token_data["uid"], update_data, session)

    if updated_book:
        book_data = BookModel.model_validate(updated_book, from_attributes=True).model_dump(mode="json")
        return SuccessResponse(status=status.HTTP_200_OK, message="Book updated successfully!", data=book_data)
    else:
        raise ErrorResponse(status=status.HTTP_404_NOT_FOUND, message="Book not found or You can't update!")
    

@book_router.delete("/{book_id}")
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session), token_data: dict = Depends(access_token_bearer)):
    book_to_delete = await book_service.delete_book(book_id, token_data["uid"], session)

    if book_to_delete:
        return SuccessResponse(status=status.HTTP_200_OK, message="Book deleted successfully!")
    else:
        raise ErrorResponse(status=status.HTTP_404_NOT_FOUND, message="Book not found or You can't delete!")
