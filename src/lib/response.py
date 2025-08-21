from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any


class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Any] = None

    class Config:
        json_encoders = {type(None): lambda v: None}


class SuccessResponse(JSONResponse):
    def __init__(self, status: int, message: str, data: Any = None):
        content = ResponseModel(success=True, message=message, data=data)
        super().__init__(status_code=status, content=content.model_dump(exclude_none=True))


class ErrorResponse(Exception):
    def __init__(self, status: int, message: str, error: Any = None):
        self.status = status
        self.message = message
        self.error = error
        super().__init__(message)
