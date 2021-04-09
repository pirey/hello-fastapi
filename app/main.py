from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from enum import Enum
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt

SECRET_KEY = "2f024061e268868b4280367bbe4417e69328f8cb86eb2c46404da28df840cde4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


def hash_password(password: str):
    return pwd_context.hash(password)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

fake_user_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "john@example",
        "hashed_password": "$2b$12$c9phP6HGmyz1j7vyL607n.mXw9KgV0gLv9Z8PcusyMoV2Ti1D1G2m",
        "disabled": False
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example",
        "hashed_password": "$2b$12$c9phP6HGmyz1j7vyL607n.mXw9KgV0gLv9Z8PcusyMoV2Ti1D1G2m",
        "disabled": True
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_user_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive User")
    return current_user


@app.post("/token", response_model=Token)
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


@app.get("/")
def index():
    return {"message": "Hello fastapi"}


@app.get("/users/me", response_model=User)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


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
