from datetime import datetime, timedelta

from fastapi import Request, APIRouter, Depends, Form, status, Response,HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import jwt

import models
from database import get_db
import dependencies
import schemas



from auth import get_current_user, authenticate_user, create_access_token, verify_password


app = APIRouter(
    tags=["notes"],
)


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
@app.post("/", response_class=HTMLResponse)
async def main(request: Request,current_user: schemas.User = Depends(get_current_user),db: Session = Depends(get_db)):
    notebooks = db.query(models.Notebook).order_by(models.Notebook.date.desc()).filter(models.Notebook.user_id==current_user.id)
    return templates.TemplateResponse("main.html", {"request": request, 'notebooks': notebooks})






@app.get("/detail/{notebook_id}", response_class=HTMLResponse)
async def detail_notebook(request: Request, notebook_id:int,db: Session = Depends(get_db)):
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
                "create_item.html", {"request": request, "errors": "Kindly login first, you are not authenticated"}
            )
        else:
            user = db.query(models.User).filter(models.User.email == email).first()
            if user is None:
                return templates.TemplateResponse(
                    "create_item.html", {"request": request, "errors": "You are not authenticated, Kindly Login"}
                )
            else:
                notebook = db.query(models.Notebook).filter(models.Notebook.id == notebook_id).first()
                if notebook.user_id != user.id:
                    return templates.TemplateResponse(
                        "detail.html", {"request": request, "errors": "Not found"}
                    )
                else:
                    return templates.TemplateResponse("detail.html", {"request": request, 'notebook': notebook})
    except Exception as e:
        pass








@app.get("/create_notebook", response_class=HTMLResponse)
async def read_notebook(request: Request):
    return templates.TemplateResponse("create_notebook.html", {"request": request})


@app.post("/create_notebook", response_class=HTMLResponse)
async def create_notebook(request: Request,
                          heading: str=Form(...),
                          content: str=Form(...),
                          db: Session = Depends(get_db)):

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
                "create_item.html", {"request": request, "errors": "Kindly login first, you are not authenticated"}
            )
        else:
            user = db.query(models.User).filter(models.User.email == email).first()
            if user is None:
                return templates.TemplateResponse(
                    "create_item.html", {"request": request, "errors": "You are not authenticated, Kindly Login"}
                )
            else:
                notes = models.Notebook(user_id=user.id, heading=heading, content=content, date=datetime.now())
                db.add(notes)
                db.commit()
                db.refresh(notes)
                response = RedirectResponse(url="/")
                return response
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "create_item.html", {"request": request, "errors": "Something is wrong !"}
        )


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(response: Response,request: Request,db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    errors = []
    if not email:
        errors.append("Please Enter valid Email")
    if not password:
        errors.append("Password enter password")
    # if len(errors) > 0:
    #     return templates.TemplateResponse(
    #         "login.html", {"request": request, "errors": errors}
    #     )
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            errors.append("Email does not exists")
            return templates.TemplateResponse(
                "login.html", {"request": request, "errors": errors}
            )
        else:
            if verify_password(password, user.password):
                data = {"sub": email}
                jwt_token = jwt.encode(
                    data, dependencies.SECRET_KEY, algorithm=dependencies.ALGORITHM
                )
                # if we redirect response in below way, it will not set the cookie
                # return responses.RedirectResponse("/?msg=Login Successfull", status_code=status.HTTP_302_FOUND)
                msg = "Login Successful"
                response = templates.TemplateResponse(
                    "login.html", {"request": request, "msg": msg}
                )
                response.set_cookie(
                    key="access_token", value=f"Bearer {jwt_token}", httponly=True
                )
                return response
            else:
                errors.append("Invalid Password")
                return templates.TemplateResponse(
                    "login.html", {"request": request, "errors": errors}
                )
    except:
        errors.append("Something Wrong while authentication or storing tokens!")
        return templates.TemplateResponse(
            "login.html", {"request": request, "errors": errors}
        )


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

