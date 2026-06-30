"""
Authentication endpoints: Azure AD (Microsoft Entra ID) login flow.
"""
import secrets
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import User, AuditLog
from app.schemas import TokenResponse, UserOut
from app.services.auth import azure_auth, jwt_service, session_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory state store (use Redis for production)
_pending_states: set[str] = set()


@router.get("/login")
async def login(request: Request):
    """Redirect to Azure AD login page."""
    state = secrets.token_urlsafe(24)
    _pending_states.add(state)

    auth_url = azure_auth.get_authorization_url(state=state)
    return RedirectResponse(auth_url)


@router.get("/callback", response_model=TokenResponse)
async def callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Azure AD callback."""
    if state not in _pending_states:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    _pending_states.discard(state)

    try:
        profile = azure_auth.exchange_code_for_token(code)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # Get or create user
    user = db.query(User).filter(User.azure_object_id == profile["azure_object_id"]).first()
    if user is None:
        user = User(
            azure_object_id=profile["azure_object_id"],
            email=profile["email"],
            display_name=profile["display_name"],
        )
        db.add(user)
    else:
        user.email = profile["email"]
        user.display_name = profile["display_name"]

    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    # Log login
    audit = AuditLog(
        user_id=user.id,
        action="LOGIN",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
        details={"method": "azure_ad"}
    )
    db.add(audit)
    db.commit()

    # Create session token
    token, expires_in = jwt_service.create_session_token(user.id, user.email)

    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserOut.model_validate(user)
    )


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user."""
    # Log logout
    audit = AuditLog(
        user_id=current_user.id,
        action="LOGOUT",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent")
    )
    db.add(audit)
    db.commit()

    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Refresh session token."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    result = jwt_service.refresh_token(token)

    if not result:
        raise HTTPException(status_code=401, detail="Unable to refresh token")

    new_token, expires_in = result
    return TokenResponse(
        access_token=new_token,
        expires_in=expires_in,
        user=UserOut.model_validate(current_user)
    )