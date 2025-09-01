from sqlmodel import SQLModel, Field, Column, Relationship, ForeignKey
from sqlalchemy import event
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, date
from typing import Optional, List

from src.lib.utils import generate_id, get_timestamp, generate_suffix 


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(sa_column=Column(pg.BIGINT, primary_key=True, index=True, nullable=False, default=generate_id))

    name: Optional[str] = Field(sa_column=Column(pg.VARCHAR(100), nullable=True, default=None))
    email: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False, unique=True))
    username: Optional[str] = Field(sa_column=Column(pg.VARCHAR(50), nullable=True, unique=True, default=None))
    password: str = Field(sa_column=Column(pg.TEXT, nullable=False), exclude=True)

    gender: str = Field(sa_column=Column(pg.ENUM("Male", "Female", "Other", name="gender"), nullable=False, default="Other"))
    image: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True, default=None))
    bio: Optional[str] = Field(sa_column=Column(pg.VARCHAR(200), nullable=True, default=None))
    setup: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=False, default=False))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=get_timestamp, nullable=False))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=get_timestamp, onupdate=get_timestamp, nullable=False))

    books: List["Book"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: List["Review"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self):
        return f"<User: {self.id} ({self.username or self.email})>"    


# Event Listener for set username (runs before INSERT)
@event.listens_for(User, "before_insert")
def set_unique_username(mapper, connection, target: User):
    """Auto-generate username if missing."""
    if not target.username or target.username.strip() == "":
        local_part = target.email.split("@")[0].split(".")[0]

        candidate = f"{local_part}_{generate_suffix()}"

        while connection.execute(
            sa.text("SELECT 1 FROM users WHERE username = :u"),
            {"u": candidate}
        ).first():
            candidate = f"{local_part}_{generate_suffix()}"

        target.username = candidate


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: int = Field(sa_column=Column(pg.BIGINT, primary_key=True, index=True, nullable=False, default=generate_id))

    title: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False, default=None))
    subtitle: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True, default=None))
    description: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True, default=None))
    thumbnail: Optional[str] = Field(sa_column=Column(pg.TEXT, nullable=True, default=None))

    author: str = Field(sa_column=Column(pg.VARCHAR(100), nullable=False, default=None))
    publisher: Optional[str] = Field(sa_column=Column(pg.VARCHAR(100), nullable=True, default=None))
    published: date = Field(sa_column=Column(pg.DATE, nullable=False, default=None))

    pages: Optional[int] = Field(sa_column=Column(pg.BIGINT, nullable=True, default=None))
    language: Optional[str] = Field(sa_column=Column(pg.VARCHAR(200), nullable=True, default=None))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=get_timestamp, nullable=False))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=get_timestamp, onupdate=get_timestamp, nullable=False))

    user_id: Optional[int] = Field(sa_column=Column(pg.BIGINT, ForeignKey("users.id"), nullable=True, default=None))
    
    reviews: List["Review"] = Relationship(back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})
    
    user: Optional[User] = Relationship(back_populates="books")

    def __repr__(self):
        return f"<Book: {self.id} ({self.title})>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: int = Field(sa_column=Column(pg.BIGINT, primary_key=True, index=True, nullable=False, default=generate_id))

    rating: int = Field(sa_column=Column(pg.INTEGER, nullable=False, default=0), lt=5)
    review: str = Field(sa_column=Column(pg.TEXT, nullable=False, default=None))
    
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=get_timestamp, nullable=False))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=get_timestamp, onupdate=get_timestamp, nullable=False))
   
    user_id: Optional[int] = Field(sa_column=Column(pg.BIGINT, ForeignKey("users.id"), nullable=True, default=None))
    book_id: Optional[int] = Field(sa_column=Column(pg.BIGINT, ForeignKey("books.id"), nullable=True, default=None))

    user: Optional[User] = Relationship(back_populates="reviews")
    book: Optional[Book] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for book {self.book_id} by user {self.user_id}>"
