from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging


logger = logging.getLogger("uvicorn.access")
logger.disabled = True


def register_middlewares(app: FastAPI):
    # Custom logging middleware
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        end_time = round(time.time() - start_time, 4)
        
        host = request.client.host
        port = request.client.port
        method = request.method
        path = request.url.path
        code = response.status_code

        print(f"{host}:{port} - {method} - {path} - {code} completed after {end_time}sec")
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[".vercel.app", ".onrender.com", "localhost", "127.0.0.1" ,"0.0.0.0"],
    )
