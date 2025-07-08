from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Any] = None

    class Config:
        json_encoders = {type(None): lambda v: None}


def success_response(status_code: int, message: str, data: Any = None):
    content = ApiResponse(success=True, message=message, data=data).model_dump(exclude_none=True)
    return JSONResponse(status_code=status_code, content=content)


def error_response(status_code: int, message: str, error: Any = None):
    content = ApiResponse(success=False, message=message, error=error).model_dump(exclude_none=True)
    return JSONResponse(status_code=status_code, content=content)
