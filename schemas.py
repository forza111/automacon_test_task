from pydantic import BaseModel

class Notebook(BaseModel):
    id: int

    class Config:
        orm_mode = True


class NotebookCreate(Notebook):
    user_id: int
    heading: str
    content: str



class AuthDetails(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int