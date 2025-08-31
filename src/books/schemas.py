from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


class BookModel(BaseModel):
    id: int
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


class BookCreateModel(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published: Optional[str]
    pages: Optional[int] = None
    language: Optional[str] = None
