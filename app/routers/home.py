from fastapi import APIRouter, HTTPException, Request, Depends
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


@router.get(
    "/activities/{activity_id}", response_class=HTMLResponse, name="activity_detail"
)
def activity_detail(request: Request, activity_id: int, db: Session = Depends(get_db)):
    item = db.get(Activity, activity_id)
    if not item:
        raise HTTPException(404, "Activity not found")
    return templates.TemplateResponse(
        "activity_detail.html", {"request": request, "a": item}
    )


@router.get("/news/{news_id}", response_class=HTMLResponse, name="news_detail")
def news_detail(request: Request, news_id: int, db: Session = Depends(get_db)):
    item = db.get(News, news_id)
    if not item:
        raise HTTPException(404, "News not found")
    return templates.TemplateResponse(
        "news_detail.html", {"request": request, "n": item}
    )
