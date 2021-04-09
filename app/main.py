from datetime import timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from app import schemas
from app.authentication import (ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user,
                                create_access_token, fake_user_db,
                                get_current_active_user)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/", tags=["Default"])
def index():
    return {"message": "Hello fastapi"}


@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(
        fake_user_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User, tags=["Users"])
def get_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/users", tags=["Users"])
def get_users(user_type: schemas.UserType):
    return {"user_type": user_type}


@app.get("/users/{user_id}", tags=["Users"])
def get_user(user_id: int):
    return {"user": f"User with the id {user_id}"}


@app.post("/items", tags=["Items"])
def create_item(item: schemas.Item):
    item_dict = item.dict()
    if item.tax:
        item_dict.update({"price_with_tax": item.price + item.tax})
    return {"item": item_dict}


@app.put("/items/{item_id}", tags=["Items"])
def update_item(item_id: int, item: schemas.Item):
    return {"item_id": item_id, **item.dict()}


@app.get("/items", tags=["Items"])
def get_items(limit: int = 10, skip: int = 0, q: Optional[str] = None):
    return {"limit": limit, "skip": skip, "q": q}


@app.get("/users/{user_id}/items", tags=["Items"])
def get_user_items(user_id: int, item_id: int, skip: int = 0, limit: int = 10, q: Optional[str] = None):
    return {"user_id": user_id, "q": q, "skip": skip, "limit": limit}


@app.get("/users/{user_id}/items/{item_id}", tags=["Items"])
def get_user_item(user_id: int, item_id: int):
    return {"user_id": user_id, "item_id": item_id}
