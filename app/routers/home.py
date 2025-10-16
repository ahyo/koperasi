from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.activity import Activity
from app.models.news import News
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="home")
def home(request: Request, db: Session = Depends(get_db)):
    latest_news = db.query(News).order_by(News.created_at.desc()).limit(3).all()
    upcoming = db.query(Activity).order_by(Activity.date.asc()).limit(3).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "news": latest_news, "activities": upcoming}
    )


@router.get("/activities", response_class=HTMLResponse, name="activities")
def activities_page(request: Request, db: Session = Depends(get_db)):
    items = db.query(Activity).order_by(Activity.date.desc()).all()
    return templates.TemplateResponse(
        "activities.html", {"request": request, "activities": items}
    )


@router.get("/news", response_class=HTMLResponse, name="news")
def news_page(request: Request, db: Session = Depends(get_db)):
    items = db.query(News).order_by(News.created_at.desc()).all()
    return templates.TemplateResponse("news.html", {"request": request, "news": items})
