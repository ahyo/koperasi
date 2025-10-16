from datetime import datetime
import os
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.member import Member
from app.config import settings
from fastapi.templating import Jinja2Templates
from werkzeug.utils import secure_filename

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["register"])

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@router.get("/register", response_class=HTMLResponse, name="register")
def register_form(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request, "errors": {}, "form": {}}
    )


@router.post("/register", response_class=HTMLResponse, name="register_submit")
async def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(""),
    dob: str = Form(""),
    occupation: str = Form(""),
    membership_type: str = Form("Reguler"),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    errors = {}
    form_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "address": address,
        "dob": dob,
        "occupation": occupation,
        "membership_type": membership_type,
    }
    if not name.strip():
        errors["name"] = "Nama wajib diisi."
    if not email.strip():
        errors["email"] = "Email wajib diisi."
    if not phone.strip():
        errors["phone"] = "No. HP wajib diisi."

    photo_path = None
    if photo and photo.filename:
        if not allowed_file(photo.filename):
            errors["photo"] = "Format foto tidak didukung (png/jpg/jpeg/gif/webp)."
        else:
            fname = secure_filename(photo.filename)
            fname = f"{int(datetime.utcnow().timestamp())}_{fname}"
            os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
            save_path = os.path.join(settings.UPLOAD_FOLDER, fname)
            with open(save_path, "wb") as f:
                f.write(await photo.read())
            photo_path = f"static/img/uploads/{fname}"

    from datetime import date as _date

    dob_date = None
    if dob.strip():
        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
        except Exception:
            errors["dob"] = "Format tanggal lahir harus YYYY-MM-DD."

    if errors:
        return templates.TemplateResponse(
            "register.html", {"request": request, "errors": errors, "form": form_data}
        )

    m = Member(
        name=name.strip(),
        email=email.lower().strip(),
        phone=phone.strip(),
        address=address.strip() if address else None,
        dob=dob_date,
        occupation=occupation.strip() if occupation else None,
        membership_type=membership_type,
        photo=photo_path,
    )

    try:
        db.add(m)
        db.commit()
        db.refresh(m)
    except Exception as e:
        db.rollback()
        if "UNIQUE" in str(e).upper():
            errors["email"] = "Email sudah terdaftar."
        else:
            errors["general"] = "Terjadi kesalahan. Coba lagi."
        return templates.TemplateResponse(
            "register.html", {"request": request, "errors": errors, "form": form_data}
        )

    return RedirectResponse(
        url=request.url_for("member_detail", member_id=m.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )
