from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import datetime
from enum import Enum


class UserSignupModel(BaseModel):
    name: str = Field(min_length=3, max_length=20)
    email: EmailStr = Field(max_length=40)
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
    email: str | None = Field(default=None, max_length=40)
    username: str | None = Field(default=None, max_length=20)
    password: str = Field(min_length=6)

    @model_validator(mode="after")
    def check_email_or_username(self) -> "UserSigninModel":
        if not self.email and not self.username:
            raise ValueError("Either email or username must be provided")
        return self


class UserModel(BaseModel):
    id: int
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



class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"


class UserUpdateModel(BaseModel):
    name: str = Field(min_length=3, max_length=20)
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-z0-9_-]{3,20}$")
    gender: GenderEnum
    bio: str | None = None

    def model_dump_filtered(self, **kwargs):
        data = self.model_dump(**kwargs)
        if self.bio is None:
            data.pop("bio", None)
        return data
    