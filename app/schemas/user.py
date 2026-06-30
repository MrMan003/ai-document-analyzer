from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    display_name: str


class UserCreate(UserBase):
    azure_object_id: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    azure_object_id: str
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime