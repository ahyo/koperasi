from typing import Optional
from fastapi import Request
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(p: str) -> str:
    return generate_password_hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return check_password_hash(hashed, p)

def get_current_user(request: Request) -> Optional[dict]:
    return request.session.get("user")

def require_role(request: Request, role: str) -> bool:
    user = get_current_user(request)
    return bool(user and user.get("role") == role)
