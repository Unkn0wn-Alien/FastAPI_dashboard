from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from database import engine, sessionlocal
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from typing import Optional
import models

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.id)
    return templates.TemplateResponse("index.html", {"request": request, "users": users})


@app.get("/addnew")
async def addnew(request: Request):
    return templates.TemplateResponse("addnew.html", {"request": request})


@app.post("/add")
async def add(request: Request, name: str = Form(...), position: str = Form(...), office: str = Form(...),
              db: Session = Depends(get_db)):
    users = models.User(name=name, position=position, office=office)
    db.add(users)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


@app.get("/edit/{user_id}")
async def edit(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "user": user})


@app.post("/update/{user_id}")
async def update(request: Request, user_id: int, name: str = Form(...), position: str = Form(...),
                 office: str = Form(...), db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.id == user_id).first()
    users.name = name
    users.position = position
    users.office = office
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


@app.get("/delete/{user_id}")
async def delete(request: Request, user_id: int, db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(users)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


@app.get("/search")
async def search(request: Request, query: Optional[str], db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.name.contains(query)).all()
    return templates.TemplateResponse("index.html", {"request": request, "users": users})


# @app.get("/user/autocomplete")
# async def autocomplete(request: Request, term: Optional[str], db: Session = Depends(get_db)):
#     users = db.query(models.User).filter(models.User.name.contains(term)).all()
#     suggestions = []
#     print(suggestions)
#     for user in users:
#         suggestions.append(user.name)
#     return suggestions
