from pydantic import BaseModel, Field, EmailStr, model_validator


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
