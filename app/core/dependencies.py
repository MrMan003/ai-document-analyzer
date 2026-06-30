"""
FastAPI dependencies for authentication/authorization.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.services.auth import jwt_service

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT."""
    token = credentials.credentials
    claims = jwt_service.decode_token(token)

    if claims is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(
        User.id == claims.get("sub"),
        User.is_active == True,
        User.is_deleted == False # type: ignore
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get the current user if authenticated, otherwise None."""
    if credentials is None:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None