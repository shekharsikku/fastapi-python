from fastapi import FastAPI
from typing import Optional
from contextlib import asynccontextmanager

from src.lib.errors import register_all_errors
from src.lib.middlewares import register_middlewares

from src.auth.routes import auth_router
from src.books.routes import book_router
from src.reviews.routes import review_router
from src.tags.routes import tag_router

from src.db.main import init_db, async_engine


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is running...!")
    await init_db()
    yield
    print("Server has been stopped...!")
    await async_engine.dispose()


version = "v1"
version_prefix =f"/api/{version}"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
"""

app = FastAPI(
    title="Bookly",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Shekhar Sharma",
        "url": "https://github.com/shekharsikku",
        "email": "shekharsikku@outlook.com",
    },
    terms_of_service="httpS://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc",
    lifespan=life_span,
    debug=True
)


register_all_errors(app)
register_middlewares(app)


app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["auth"])
app.include_router(book_router, prefix=f"{version_prefix}/books", tags=["books"])
app.include_router(review_router, prefix=f"{version_prefix}/reviews", tags=["reviews"])
app.include_router(tag_router, prefix=f"{version_prefix}/tags", tags=["tags"])


@app.get("/")
@app.get("/hello")
def say_hello(name: Optional[str] = "User") -> dict:
    return {"message": f"Hello, {name}!"}
