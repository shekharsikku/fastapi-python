from pydantic import BaseModel, Field, EmailStr


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
