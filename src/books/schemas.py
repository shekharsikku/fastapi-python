from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List


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
    def cast_id_to_str(cls, v):
        return str(v)


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
