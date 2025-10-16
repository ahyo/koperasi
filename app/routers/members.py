from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.member import Member
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/members", tags=["members"])

@router.get("", response_class=HTMLResponse, name="members")
def list_members(request: Request, q: str = Query("", alias="q"), db: Session = Depends(get_db)):
    query = db.query(Member)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(Member.name.ilike(like))
    items = query.order_by(Member.created_at.desc()).all()
    return templates.TemplateResponse("member_list.html", {"request": request, "members": items, "q": q})

@router.get("/{member_id}", response_class=HTMLResponse, name="member_detail")
def member_detail(request: Request, member_id: int, db: Session = Depends(get_db)):
    m = db.get(Member, member_id)
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")
    return templates.TemplateResponse("member_detail.html", {"request": request, "m": m})
