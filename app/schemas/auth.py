from typing import Optional
from pydantic import BaseModel

from app.schemas.user import UserOut


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class LoginResponse(BaseModel):
    message: str
    redirect_url: Optional[str] = None