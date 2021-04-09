from datetime import timedelta

from app import authentication, database, schemas, models
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(tags=["Authentication"])

def log_login_activity(user: models.User):
    with open(".log", mode="a") as log:
        log.write(f"New user login: {user.username}")


@router.post("/token", response_model=schemas.Token)
async def login(background_tasks: BackgroundTasks, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = authentication.authenticate_user(
        db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(
        minutes=authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = authentication.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    background_tasks.add_task(log_login_activity, user)

    return schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )
