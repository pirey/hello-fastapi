from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from enum import Enum
from pydantic import BaseModel

app = FastAPI()

fake_user_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "john@example",
        "hashed_password": "fakehashedsecret",
        "disabled": False
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example",
        "hashed_password": "fakehashedsecret",
        "disabled": True
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserType(str, Enum):
    admin = "admin"
    customer = "customer"


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def fake_hash_password(password: str):
    return "fakehashed" + password


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    user = get_user(fake_user_db, token)
    return user


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive User")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_user_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/")
def index():
    return {"message": "Hello fastapi"}


@app.get("/users/me")
def get_me(current_user: User = Depends(get_current_active_user)):
    return {"user": current_user}


@app.get("/users")
def get_users(user_type: UserType):
    return {"user_type": user_type}


@app.get("/users/{user_id}")
def get_users(user_id: int):
    return {"user": f"User with the id {user_id}"}


@app.post("/items")
def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        item_dict.update({"price_with_tax": item.price + item.tax})
    return {"item": item_dict}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}


@app.get("/items")
def get_items(limit: int = 10, skip: int = 0, q: Optional[str] = None):
    return {"limit": limit, "skip": skip, "q": q}


@app.get("/users/{user_id}/items")
def get_user_items(user_id: int, item_id: int, skip: int = 0, limit: int = 10, q: Optional[str] = None):
    return {"user_id": user_id, "q": q, "skip": skip, "limit": limit}


@app.get("/users/{user_id}/items/{item_id}")
def get_user_item(user_id: int, item_id: int):
    return {"user_id": user_id, "item_id": item_id}
