from pydantic import BaseModel, Field, EmailStr, model_validator, field_validator
from datetime import datetime
from typing import List
from enum import Enum

from src.books.schemas import BookModel
from src.reviews.schemas import ReviewModel


class UserSignupModel(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Example",
                "email": "example@mail.ai",
                "password": "Example@123",
            }
        }
    }


class UserSigninModel(BaseModel):
    email: str | None = None
    username: str | None = None
    password: str = Field(min_length=1)

    @model_validator(mode="after")
    def check_email_or_username(self) -> "UserSigninModel":
        if not self.email and not self.username:
            raise ValueError("Either email or username must be provided")
        return self


class UserModel(BaseModel):
    id: str
    name: str | None
    email: str
    username: str | None
    password: str = Field(exclude=True)
    gender: str | None
    image: str | None
    bio: str | None
    setup: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def cast_id_to_str(cls, v):
        return str(v)


class UserBooksReviewsModel(UserModel):
    books: List[BookModel]
    reviews: List[ReviewModel]


class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"


class UserUpdateModel(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    username: str = Field(min_length=3, max_length=25, pattern=r"^[a-z0-9_-]{3,20}$")
    gender: GenderEnum
    bio: str | None = Field(max_length=200, default=None)

    def model_dump_filtered(self, **kwargs):
        data = self.model_dump(**kwargs)
        if self.bio is None:
            data.pop("bio", None)
        return data
    

class ChangePasswordModel(BaseModel):
    old_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6)
