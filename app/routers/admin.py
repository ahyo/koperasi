from datetime import datetime
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from sqlalchemy.orm import Session

from app.auth import require_role
from app.database import get_db
from app.models.activity import Activity
from app.models.news import News
from app.models.member import Member
from app.config import settings

from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from werkzeug.utils import secure_filename

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/admin", tags=["admin"])

security = HTTPBasic()


def require_admin(request: Request):
    if not require_role(request, "admin"):
        # user belum login / bukan admin -> tolak tanpa WWW-Authenticate
        raise HTTPException(status_code=403, detail="Forbidden")
    return True


# ---------- Dashboard ----------
@router.get("", response_class=HTMLResponse, name="admin_dashboard")
def dashboard(
    request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)
):
    stats = {
        "members": db.query(Member).count(),
        "activities": db.query(Activity).count(),
        "news": db.query(News).count(),
    }
    return templates.TemplateResponse(
        "admin/dashboard.html", {"request": request, "stats": stats}
    )


# ---------- Activities CRUD ----------
@router.get("/activities", response_class=HTMLResponse, name="admin_activities")
def activities_list(
    request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)
):
    items = db.query(Activity).order_by(Activity.date.desc()).all()
    return templates.TemplateResponse(
        "admin/activities_list.html", {"request": request, "items": items}
    )


@router.get("/activities/new", response_class=HTMLResponse, name="admin_activity_new")
def activity_new(request: Request, _: bool = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/activities_form.html", {"request": request, "item": None}
    )


@router.post("/activities/new", response_class=HTMLResponse)
def activity_create(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    date: str = Form(...),
    location: str = Form(""),
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    from datetime import datetime

    try:
        d = datetime.strptime(date, "%Y-%m-%d").date()
    except Exception:
        return templates.TemplateResponse(
            "admin/activities_form.html",
            {
                "request": request,
                "item": None,
                "error": "Format tanggal harus YYYY-MM-DD",
            },
        )
    obj = Activity(
        title=title.strip(),
        description=description.strip(),
        date=d,
        location=location.strip() or None,
    )
    db.add(obj)
    db.commit()
    return RedirectResponse(
        url=request.url_for("admin_activities"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get(
    "/activities/{id}/edit", response_class=HTMLResponse, name="admin_activity_edit"
)
def activity_edit(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = db.get(Activity, id)
    if not obj:
        from fastapi import HTTPException

        raise HTTPException(404, "Not found")
    return templates.TemplateResponse(
        "admin/activities_form.html", {"request": request, "item": obj}
    )


@router.post("/activities/{id}/edit", response_class=HTMLResponse)
def activity_update(
    request: Request,
    id: int,
    title: str = Form(...),
    description: str = Form(...),
    date: str = Form(...),
    location: str = Form(""),
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = db.get(Activity, id)
    if not obj:
        from fastapi import HTTPException

        raise HTTPException(404, "Not found")
    try:
        d = datetime.strptime(date, "%Y-%m-%d").date()
    except Exception:
        return templates.TemplateResponse(
            "admin/activities_form.html",
            {
                "request": request,
                "item": obj,
                "error": "Format tanggal harus YYYY-MM-DD",
            },
        )
    obj.title = title.strip()
    obj.description = description.strip()
    obj.date = d
    obj.location = location.strip() or None
    db.commit()
    return RedirectResponse(
        url=request.url_for("admin_activities"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/activities/{id}/delete")
def activity_delete(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = db.get(Activity, id)
    if obj:
        db.delete(obj)
        db.commit()
    return RedirectResponse(
        url=request.url_for("admin_activities"), status_code=status.HTTP_303_SEE_OTHER
    )


# ---------- News CRUD ----------
@router.get("/news", response_class=HTMLResponse, name="admin_news")
def news_list(
    request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)
):
    items = db.query(News).order_by(News.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/news_list.html", {"request": request, "items": items}
    )


@router.get("/news/new", response_class=HTMLResponse, name="admin_news_new")
def news_new(request: Request, _: bool = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/news_form.html", {"request": request, "item": None}
    )


@router.post("/news/new", response_class=HTMLResponse)
def news_create(
    request: Request,
    title: str = Form(...),
    body: str = Form(...),
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = News(title=title.strip(), body=body.strip())
    db.add(obj)
    db.commit()
    return RedirectResponse(
        url=request.url_for("admin_news"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/news/{id}/edit", response_class=HTMLResponse, name="admin_news_edit")
def news_edit(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = db.get(News, id)
    if not obj:
        from fastapi import HTTPException

        raise HTTPException(404, "Not found")
    return templates.TemplateResponse(
        "admin/news_form.html", {"request": request, "item": obj}
    )


@router.post("/news/{id}/edit", response_class=HTMLResponse)
def news_update(
    request: Request,
    id: int,
    title: str = Form(...),
    body: str = Form(...),
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = db.get(News, id)
    if not obj:
        from fastapi import HTTPException

        raise HTTPException(404, "Not found")
    obj.title = title.strip()
    obj.body = body.strip()
    db.commit()
    return RedirectResponse(
        url=request.url_for("admin_news"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/news/{id}/delete")
def news_delete(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = db.get(News, id)
    if obj:
        db.delete(obj)
        db.commit()
    return RedirectResponse(
        url=request.url_for("admin_news"), status_code=status.HTTP_303_SEE_OTHER
    )


# ---------- Members CRUD (basic) ----------
@router.get("/members", response_class=HTMLResponse, name="admin_members")
def members_list(
    request: Request, db: Session = Depends(get_db), _: bool = Depends(require_admin)
):
    items = db.query(Member).order_by(Member.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/members_list.html", {"request": request, "items": items}
    )


@router.get("/members/{id}/edit", response_class=HTMLResponse, name="admin_member_edit")
def member_edit(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = db.get(Member, id)
    if not obj:
        from fastapi import HTTPException

        raise HTTPException(404, "Not found")
    return templates.TemplateResponse(
        "admin/members_form.html", {"request": request, "item": obj}
    )


@router.post("/members/{id}/edit", response_class=HTMLResponse)
async def member_update(
    request: Request,
    id: int,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    membership_type: str = Form("Reguler"),
    address: str = Form(""),
    occupation: str = Form(""),
    dob: str = Form(""),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = db.get(Member, id)
    if not obj:
        from fastapi import HTTPException

        raise HTTPException(404, "Not found")

    obj.name = name.strip()
    obj.email = email.lower().strip()
    obj.phone = phone.strip()
    obj.membership_type = membership_type
    obj.address = address.strip() or None
    obj.occupation = occupation.strip() or None

    if dob.strip():
        try:
            obj.dob = datetime.strptime(dob, "%Y-%m-%d").date()
        except Exception:
            pass

    if photo and photo.filename:
        fname = secure_filename(photo.filename)
        fname = f"{int(datetime.utcnow().timestamp())}_{fname}"
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
        save_path = os.path.join(settings.UPLOAD_FOLDER, fname)
        with open(save_path, "wb") as f:
            f.write(await photo.read())
        obj.photo = f"static/img/uploads/{fname}"

    db.commit()
    return RedirectResponse(
        url=request.url_for("admin_members"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/members/{id}/delete")
def member_delete(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    obj = db.get(Member, id)
    if obj:
        db.delete(obj)
        db.commit()
    return RedirectResponse(
        url=request.url_for("admin_members"), status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/members/{id}/card", response_class=HTMLResponse, name="admin_member_card")
def member_card(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin),
):
    m = db.get(Member, id)
    if not m:
        raise HTTPException(status_code=404, detail="Member not found")
    return templates.TemplateResponse(
        "admin/member_card.html", {"request": request, "m": m}
    )
