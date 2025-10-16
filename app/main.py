import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app.models.activity import Activity
from app.models.news import News
from app.routers.home import router as home_router
from app.routers.members import router as members_router
from app.routers.register import router as register_router
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from sqlalchemy.orm import Session
from datetime import date

app = FastAPI(title="Koperasi Kita - FastAPI")
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home_router)
app.include_router(members_router)
app.include_router(register_router)
app.include_router(admin_router)
app.include_router(auth_router)

@app.on_event("startup")
def on_startup():
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        if not db.query(Activity).first():
            db.add_all([
                Activity(title="Rapat Anggota Tahunan", description="Pembahasan laporan keuangan dan program kerja.", date=date(2025,3,15), location="Aula Koperasi"),
                Activity(title="Pelatihan UMKM", description="Workshop pemasaran digital untuk anggota.", date=date(2025,5,20), location="Ruang Pelatihan"),
            ])
        if not db.query(News).first():
            db.add_all([
                News(title="Koperasi Luncurkan Program Simpanan Berjangka", body="Program baru dengan bunga kompetitif untuk anggota."),
                News(title="Kerja Sama dengan Bank Lokal", body="Mempermudah akses modal bagi anggota UMKM."),
            ])
    # ensure default admin user exists
    from app.models.user import User
    from app.auth import hash_password
    username = os.environ.get("ADMIN_USER", "admin")
    password = os.environ.get("ADMIN_PASS", "admin123")
    existing = db.query(User).filter(User.username == username).first()
    if not existing:
        db.add(User(username=username, password_hash=hash_password(password), role="admin"))
        db.commit()
        db.commit()
