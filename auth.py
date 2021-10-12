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


templates = Jinja2Templates(directory="templates")

async def get_current_user(request: Request,db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "To view this page, you need to log in"}
        )
    scheme, _, param = token.partition(" ")
    payload = jwt.decode(param, dependencies.SECRET_KEY, algorithms=dependencies.ALGORITHM)
    email = payload.get("sub")
    if email is None:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "To view this page, you need to log in"}
        )
    else:
        user = db.query(models.User).filter(models.User.email == email).first()
        return user



def create_access_token(data: dict,request: Request):
    jwt_token = jwt.encode(data, dependencies.SECRET_KEY, algorithm=dependencies.ALGORITHM)
    msg = "Login Successful"
    response = templates.TemplateResponse("main.html", {"request": request, "msg": msg})
    response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
    return response


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_password_hash(password):
    return dependencies.pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return dependencies.pwd_context.verify(plain_password, hashed_password)