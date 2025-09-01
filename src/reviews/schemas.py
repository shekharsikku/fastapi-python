from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewModel(BaseModel):
    id: int
    rating: int = Field(lt=5)
    review: str
    user_id: Optional[int]
    book_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class ReviewCreateModel(BaseModel):
    rating: int = Field(lt=5)
    review: str
