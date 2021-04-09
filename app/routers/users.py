from typing import List

from app import database, schemas, authentication
from app.repositories import user as user_repository
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])



@router.get("/me", response_model=schemas.User)
def get_me(current_user: schemas.User = Depends(authentication.get_current_active_user)):
    return current_user


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    return user_repository.create_user(db, user)


@router.get("/", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 10, current_user: schemas.User = Depends(authentication.get_current_active_user), db: Session = Depends(database.get_db)):
    users = user_repository.get_users(db, skip, limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, current_user: schemas.User = Depends(authentication.get_current_active_user), db: Session = Depends(database.get_db)):
    user = user_repository.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
