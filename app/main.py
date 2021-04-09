from fastapi import FastAPI
from typing import Optional
from enum import Enum

app = FastAPI()

class UserType(str, Enum):
    admin = "admin"
    customer = "customer"

@app.get("/")
def index():
    return {"message": "Hello fastapi"}


@app.get("/users/me")
def get_me():
    return {"user": "current user"}

@app.get("/users")
def get_users(user_type: UserType):
    return {"user_type": user_type}


@app.get("/users/{user_id}")
def get_users(user_id: int):
    return {"user": f"User with the id {user_id}"}


@app.get("/items")
def get_items(limit: int = 10, skip: int = 0, q: Optional[str] = None):
    return {"limit": limit, "skip": skip, "q": q}


@app.get("/users/{user_id}/items")
def get_user_items(user_id: int, item_id: int, skip: int = 0, limit: int = 10, q: Optional[str] = None):
    return {"user_id": user_id, "q": q, "skip": skip, "limit": limit}


@app.get("/users/{user_id}/items/{item_id}")
def get_user_item(user_id: int, item_id: int):
    return {"user_id": user_id, "item_id": item_id}
