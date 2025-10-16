import os
from pydantic import BaseModel


class Settings(BaseModel):
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-koperasi-secret")
    DATABASE_URL: str = (
        os.environ.get("DATABASE_URL")
        or "mysql+pymysql://syae2437_koperasi:Ayocool123$%@localhost:3306/syae2437_koperasi"
    )
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER") or "app/static/img/uploads"
    MAX_CONTENT_LENGTH_MB: int = int(os.environ.get("MAX_CONTENT_LENGTH_MB", "4"))


settings = Settings()
