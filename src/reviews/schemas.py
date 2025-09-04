from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class ReviewModel(BaseModel):
    id: str
    rating: float = Field(le=5)
    review: str
    user_id: Optional[str]
    book_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_validator("id", "user_id", "book_id", mode="before")
    @classmethod
    def cast_id_to_str(cls, v):
        return str(v)


class ReviewCreateModel(BaseModel):
    rating: float = Field(le=5)
    review: str
