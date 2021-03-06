from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config, database
from app.routers import authentication as auth_router
from app.routers import items, users

# TODO: use alembic for database setup and migration
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Hello Fastapi",
    version="1.0.0",
    docs_url="/"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(auth_router.router)
app.include_router(items.router)
app.include_router(users.router)


@app.get("/version")
def get_version():
    return {"title": "Hello Fastapi", "version": "1.0.0"}


@app.get("/settings")
def display_settings():
    settings = config.get_settings()
    return settings.dict()
