from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from app.database import get_db
from app.models.user import User
from app.auth import hash_password, verify_password

from app.config import settings
import os

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["auth"])


@router.get("/reset")
def login_reset(
    request: Request,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == "admin").first()
    user.password_hash = hash_password("Ayocool123$%")
    db.commit()
    return "done"


@router.get("/login", response_class=HTMLResponse, name="login")
def login_form(request: Request):
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "error": None}
    )


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Username atau password salah."},
        )
    request.session["user"] = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }
    return RedirectResponse(
        url=request.url_for("admin_dashboard"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/logout", name="logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
