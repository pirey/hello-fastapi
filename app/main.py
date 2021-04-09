from datetime import timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

from app import schemas, database
from app.repositories import user as user_repository, item as item_repository
from app.authentication import (ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user,
                                create_access_token,
                                get_current_active_user)

database.Base.metadata.create_all(bind=database.engine)

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
    return "Hello Fastapi"


@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
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


# USER
@app.get("/users/me", response_model=schemas.User, tags=["Users"])
def get_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.post("/users", tags=["Users"], response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    return user_repository.create_user(db, user)


@app.get("/users", tags=["Users"], response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 10, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(database.get_db)):
    users = user_repository.get_users(db, skip, limit)
    return users


@app.get("/users/{user_id}", tags=["Users"], response_model=schemas.User)
def get_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(database.get_db)):
    user = user_repository.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# ITEM
@app.post("/items", tags=["Items"], response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(database.get_db)):
    return item_repository.create_user_item(db, current_user, item)

@app.get("/items", tags=["Items"], response_model=List[schemas.Item])
def get_items(skip: int = 0, limit: int = 10, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(database.get_db)):
    items = item_repository.get_user_items(db, current_user, skip, limit)
    return items


@app.get("/items/{item_id}", tags=["Items"], response_model=schemas.Item)
def get_item(item_id: int, current_user: schemas.User = Depends(get_current_active_user), db: Session = Depends(database.get_db)):
    item = item_repository.get_user_item(db, current_user, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item