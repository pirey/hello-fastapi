from typing import List

from app import authentication, database, schemas
from app.repositories import item as item_repository
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, current_user: schemas.User = Depends(authentication.get_current_active_user), db: Session = Depends(database.get_db)):
    return item_repository.create_user_item(db, current_user, item)


@router.get("/", response_model=List[schemas.Item])
def get_items(skip: int = 0, limit: int = 10, current_user: schemas.User = Depends(authentication.get_current_active_user), db: Session = Depends(database.get_db)):
    items = item_repository.get_user_items(db, current_user, skip, limit)
    return items


@router.get("/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, current_user: schemas.User = Depends(authentication.get_current_active_user), db: Session = Depends(database.get_db)):
    item = item_repository.get_user_item(db, current_user, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item
