import uuid
from datetime import date, datetime
from typing import List

from pydantic import BaseModel

from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel


class BookModel(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookDetailModel(BookModel):
    reviews: List[ReviewModel]
    tags:List[TagModel]


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
