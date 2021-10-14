from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Depends,Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from jose import jwt

import dependencies
import models
import database

templates = Jinja2Templates(directory="templates")


class Authenticate:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = get_user_by_email(db, email)
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        return user

    @staticmethod
    async def get_current_user(request: Request,db: Session = Depends(database.get_db)):
        token = request.cookies.get("access_token")
        if token is None:
            return None
        scheme, _, param = token.partition(" ")
        payload = jwt.decode(param, dependencies.SECRET_KEY, algorithms=dependencies.ALGORITHM)
        email = payload.get("sub")
        user = db.query(models.User).filter(models.User.email == email).first()
        return user

    @staticmethod
    def create_access_token(data: dict,request: Request):
        jwt_token = jwt.encode(data, dependencies.SECRET_KEY, algorithm=dependencies.ALGORITHM)
        response = RedirectResponse(url="/")
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