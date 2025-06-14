import uuid
from datetime import date, datetime, timezone
from typing import List, Optional

from sqlmodel import SQLModel
from sqlmodel import Column, Field, Relationship, SQLModel
import sqlalchemy.dialects.mysql as mysql 


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: uuid.UUID = Field(sa_column=Column(mysql.VARCHAR(36), primary_key=True, nullable=False, default=lambda: str(uuid.uuid4())))

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

    created_at: datetime = Field(sa_column=Column(mysql.TIMESTAMP, default=lambda: datetime.now(timezone.utc)))
    updated_at: datetime = Field(sa_column=Column(mysql.TIMESTAMP, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)))

    def __repr__(self):
        return f"<Book {self.title}>"
    