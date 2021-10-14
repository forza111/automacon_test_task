from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Depends,Request
from fastapi.templating import Jinja2Templates
from jose import jwt

import dependencies
import models
import database

templates = Jinja2Templates(directory="templates")


class Authenticate:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        '''
        The function takes 2 arguments - email and password. The first step is to search the database by email,
        if there is no user with such email, the function returns False. If a user with such an email exists, the
        password is checked (entered in the form and in the database, which is hashed).
        If the password is incorrect, it returns False, if everything went well, then it returns the user
        '''
        user = Authenticate.get_user_by_email(db, email)
        if not user:
            return False
        if not Authenticate.verify_password(password, user.password):
            return False
        return user

    @staticmethod
    async def get_current_user(request: Request,db: Session = Depends(database.get_db)):
        '''Checks cookies for the presence of a token. in the absence of a token, returns to None. If a valid token
        is found, will return the authorized user.'''
        token = request.cookies.get("access_token")
        if token is None:
            return None
        scheme, _, param = token.partition(" ")
        payload = jwt.decode(param, dependencies.SECRET_KEY, algorithms=dependencies.ALGORITHM)
        email = payload.get("sub")
        user = Authenticate.get_user_by_email(db,email)
        return user

    @staticmethod
    def create_access_token(data: dict,request: Request):
        '''Token creation. The function accepts data in the form of a dictionary'''
        jwt_token = jwt.encode(data, dependencies.SECRET_KEY, algorithm=dependencies.ALGORITHM)
        response = RedirectResponse(url="/")
        response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
        return response

    @staticmethod
    def get_user(db: Session, user_id: int):
        '''Get user by id'''
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        '''Get user by email'''
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def get_password_hash(password):
        '''Hash password'''
        return dependencies.pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        '''Check password and hash password version'''
        return dependencies.pwd_context.verify(plain_password, hashed_password)