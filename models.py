from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True)
    password = Column(String)



class Notebook(Base):
    __tablename__ = "notebook"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref("user_notebook"))

    heading = Column(String(50))
    content = Column(Text)
    date = Column(DateTime)