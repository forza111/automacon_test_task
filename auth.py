from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import Depends,Request
from fastapi.templating import Jinja2Templates
from jose import jwt
import database

import dependencies
import models


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# async def get_current_user(db: Session = Depends(database.get_db),token: str = Depends(dependencies.oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, dependencies.SECRET_KEY, algorithms=[dependencies.ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = username
#     except JWTError:
#         raise credentials_exception
#     user = get_user_by_email(db,email=token_data)
#     if user is None:
#         raise credentials_exception
#     return user

templates = Jinja2Templates(directory="templates")

async def get_current_user(request: Request,db: Session = Depends(database.get_db)):
    try:
        token = request.cookies.get("access_token")
        if not token:
            return templates.TemplateResponse(
                "create_item.html", {"request": request, "errors": "Kindly Authenticate first by login"}
            )
        scheme, _, param = token.partition(" ")
        payload = jwt.decode(param, dependencies.SECRET_KEY, algorithms=dependencies.ALGORITHM)
        email = payload.get("sub")
        if email is None:
            return templates.TemplateResponse(
                "login.html", {"request": request, "errors": "Kindly login first, you are not authenticated"}
            )
        else:
            user = db.query(models.User).filter(models.User.email == email).first()
            return user
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "detail.html", {"request": request, "errors": "Something is wrong !"}
        )



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, dependencies.SECRET_KEY, algorithm=dependencies.ALGORITHM)
    return encoded_jwt


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_password_hash(password):
    return dependencies.pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return dependencies.pwd_context.verify(plain_password, hashed_password)