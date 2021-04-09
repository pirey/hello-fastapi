from sqlalchemy.orm import Session

from app import models, schemas, authentication

def get_user_item(db: Session, user: models.User, item_id: int):
    return db.query(models.Item).join(models.Item.owner).filter(models.User.id == user.id).filter(models.Item.id == item_id).first()

def get_user_items(db: Session, user: models.User, skip: int = 0, limit: int = 10):
    return db.query(models.Item).join(models.Item.owner).filter(models.User.id == user.id).offset(skip).limit(limit).all()

def create_user_item(db: Session, user: models.User, item: schemas.ItemCreate):
    new_item = models.Item(
        title=item.title,
        description=item.description,
        owner_id=user.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item
