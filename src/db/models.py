from uuid import UUID
from typing import List, Optional
from datetime import date, datetime

from sqlmodel import SQLModel
from sqlmodel import Column, Field, Relationship, SQLModel
import sqlalchemy.dialects.mysql as mysql

from src.lib.utils import generate_uuid, get_timestamp


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(sa_column=Column(mysql.VARCHAR(36), primary_key=True, nullable=False, default=generate_uuid()))

    username: str
    email: str
    name: str
    role: str = Field(sa_column=Column(mysql.VARCHAR(10), nullable=False, server_default="user"))
    password: str = Field(sa_column=Column(mysql.VARCHAR(255), nullable=False), exclude=True)
    verified: bool = False

    created_at: datetime = Field(sa_column=Column(mysql.TIMESTAMP, default=get_timestamp()))
    updated_at: datetime = Field(sa_column=Column(mysql.TIMESTAMP, default=get_timestamp(), onupdate=get_timestamp()))

    def __repr__(self):
        return f"<User {self.username}>"
    

class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: UUID = Field(sa_column=Column(mysql.VARCHAR(36), primary_key=True, nullable=False, default=generate_uuid()))

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

    created_at: datetime = Field(sa_column=Column(mysql.TIMESTAMP, default=get_timestamp()))
    updated_at: datetime = Field(sa_column=Column(mysql.TIMESTAMP, default=get_timestamp(), onupdate=get_timestamp()))

    def __repr__(self):
        return f"<Book {self.title}>"
    