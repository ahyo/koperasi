from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    dob: Optional[date] = None
    occupation: Optional[str] = None
    membership_type: str = "Reguler"

class MemberOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    dob: Optional[date] = None
    occupation: Optional[str] = None
    membership_type: str
    photo: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
