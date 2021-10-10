from pydantic import BaseModel

class Notebook(BaseModel):
    id: int

    class Config:
        orm_mode = True


class NotebookCreate(Notebook):
    user_id: int
    heading: str
    content: str