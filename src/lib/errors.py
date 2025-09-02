from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .response import ResponseModel, ErrorResponse


async def error_response_handler(request: Request, exc: ErrorResponse):
    content = ResponseModel(success=False, message=exc.message, error=exc.error)
    return JSONResponse(status_code=exc.status, content=content.model_dump(exclude_none=True))


def register_all_errors(app: FastAPI):
    app.add_exception_handler(ErrorResponse, error_response_handler)

    @app.exception_handler(HTTPException)
    async def http_error_handler(request, exc: HTTPException):
        content = ResponseModel(success=False, message=f"{exc.detail}!")
        return JSONResponse(status_code=exc.status_code, content=content.model_dump(exclude_none=True))

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request, exc: SQLAlchemyError):
        print(f"Database Error: {str(exc)}")
        content = ResponseModel(success=False, message="Database error occurred!")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content.model_dump(exclude_none=True))
