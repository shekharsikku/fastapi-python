from sqlmodel import Column, Field, Relationship, SQLModel, ForeignKey
from sqlmodel import SQLModel
from sqlalchemy import event
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime

from src.lib.utils import generate_id, get_timestamp, generate_suffix 


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(sa_column=Column(pg.BIGINT, primary_key=True, index=True, nullable=False, default=generate_id))

    name: str | None = Field(sa_column=Column(pg.VARCHAR(20), nullable=True, default=None))
    email: str = Field(sa_column=Column(pg.VARCHAR(40), nullable=False, unique=True))
    username: str | None = Field(sa_column=Column(pg.VARCHAR(20), nullable=True, unique=True, default=None))
    password: str = Field(sa_column=Column(pg.VARCHAR(255), nullable=False), exclude=True)

    gender: str | None = Field(sa_column=Column(pg.ENUM("Male", "Female", "Other", name="gender_enum"), nullable=True, default="Other"))
    image: str | None = Field(sa_column=Column(pg.TEXT, nullable=True, default=None))
    bio: str | None = Field(sa_column=Column(pg.VARCHAR(255), nullable=True, default=None))
    setup: bool = Field(sa_column=Column(pg.BOOLEAN, nullable=True, default=False))

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=get_timestamp, nullable=False))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP(timezone=True), default=get_timestamp, onupdate=get_timestamp, nullable=False))

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
