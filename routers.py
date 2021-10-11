from datetime import datetime, timedelta

from fastapi import FastAPI, Request, APIRouter, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models
from database import get_db
import schemas
import dependencies



from fastapi import FastAPI, Depends, HTTPException
from auth import get_current_user, authenticate_user, create_access_token
from schemas import AuthDetails


# auth_handler = AuthHandler()




app = APIRouter(
    tags=["notes"],
)


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
@app.post("/", response_class=HTMLResponse)
async def main(request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    notebooks = db.query(models.Notebook).order_by(models.Notebook.date.desc()).all()
    return templates.TemplateResponse("main.html", {"request": request, 'notebooks': notebooks})


@app.get("/detail/{notebook_id}", response_class=HTMLResponse)
async def detail_notebook(request: Request, notebook_id:int,db: Session = Depends(get_db)):
    notebook = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    return templates.TemplateResponse("detail.html", {"request": request, 'notebook': notebook})


@app.get("/create_notebook", response_class=HTMLResponse)
async def read_notebook(request: Request):
    return templates.TemplateResponse("create_notebook.html", {"request": request})


@app.post("/create_notebook", response_class=HTMLResponse)
async def create_notebook(heading: str=Form(...),
                          content: str=Form(...),
                          db: Session = Depends(get_db)):
    notes = models.Notebook(user_id=1,heading=heading,content=content, date=datetime.now())
    db.add(notes)
    db.commit()
    db.refresh(notes)
    response = RedirectResponse(url="/")
    return response



@app.post("/login", response_class=HTMLResponse)
async def login_for_access_token(db: Session = Depends(get_db),
                                 form_data: dependencies.OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=dependencies.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}