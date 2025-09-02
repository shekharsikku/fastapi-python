from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List

from src.reviews.schemas import ReviewModel


class BookModel(BaseModel):
    id: str
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    thumbnail: Optional[str]
    author: Optional[str]
    publisher: Optional[str]
    published: Optional[date]
    pages: Optional[int]
    language: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def cast_id_to_str(cls, v):
        return str(v)


class BookBaseModel(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published: Optional[date] = None
    pages: Optional[int] = None
    language: Optional[str] = None

    @field_validator("published", mode="before")
    @classmethod
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        return v


class BookCreateModel(BookBaseModel):
    title: str
    author: str
    published: date


class BookUpdateModel(BookBaseModel):
    pass


class BookDetailModel(BookModel):
    reviews: List[ReviewModel]
