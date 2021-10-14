from datetime import datetime

from fastapi import Request, APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models
from database import get_db
import schemas
from auth import Authenticate


app = APIRouter(tags=["notes"])
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
@app.post("/", response_class=HTMLResponse)
async def main(request: Request,current_user: schemas.User = Depends(Authenticate.get_current_user),db: Session = Depends(get_db)):
    if current_user is None:
        response = RedirectResponse(url="/login")
        return response
    notebooks = db.query(models.Notebook).order_by(models.Notebook.date.desc()).filter(models.Notebook.user_id==current_user.id)
    return templates.TemplateResponse("main.html", {"request": request, 'notebooks': notebooks})


@app.get("/detail/{notebook_id}", response_class=HTMLResponse)
async def detail_notebook(
        request: Request,
        notebook_id:int,
        current_user: schemas.User = Depends(Authenticate.get_current_user),
        db: Session = Depends(get_db)
):
    if current_user is None:
        response = RedirectResponse(url="/login")
        return response
    notebook = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
    if notebook is None:
        return templates.TemplateResponse("404.html", {"request": request})
    elif notebook.user_id != current_user.id:
        return templates.TemplateResponse("404.html", {"request": request})
    else:
        return templates.TemplateResponse("detail.html", {"request": request, 'notebook': notebook})



@app.get("/create_notebook", response_class=HTMLResponse)
async def read_notebook(request: Request):
    return templates.TemplateResponse("create_notebook.html", {"request": request})


@app.post("/create_notebook", response_class=HTMLResponse)
async def create_notebook(
        request: Request,
        heading: str=Form(...),
        content: str=Form(...),
        current_user: schemas.User = Depends(Authenticate.get_current_user),
        db: Session = Depends(get_db)
):
    if current_user is None:
        response = RedirectResponse(url="/login")
        return response
    notes = models.Notebook(user_id=current_user.id, heading=heading, content=content, date=datetime.now())
    db.add(notes)
    db.commit()
    db.refresh(notes)
    response = RedirectResponse(url="/")
    return response



@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request,db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    errors = []
    if not email:
        errors.append("Please Enter valid Email")
    if not password:
        errors.append("Password enter password")
    if len(errors) > 0:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": errors}
        )
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            errors.append("Email does not exists")
            return templates.TemplateResponse(
                "login.html", {"request": request, "error": errors}
            )
        else:
            if Authenticate.verify_password(password, user.password):
                data = {"sub": email}
                response = Authenticate.create_access_token(data,request)
                return response
            else:
                errors.append("Invalid Password")
                return templates.TemplateResponse(
                    "login.html", {"request": request, "error": errors}
                )
    except:
        errors.append("Something Wrong while authentication or storing tokens!")
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": errors}
        )