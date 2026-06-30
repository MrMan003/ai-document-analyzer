"""
Azure AD authentication integration.
"""
from typing import Dict, Any, Optional
import msal

from app.core.config import settings


class AzureAuthService:
    """Azure AD authentication service."""

    def __init__(self):
        self.client_id = settings.AZURE_CLIENT_ID
        self.client_secret = settings.AZURE_CLIENT_SECRET
        self.tenant_id = settings.AZURE_TENANT_ID
        self.redirect_uri = settings.AZURE_REDIRECT_URI
        self.authority = settings.azure_authority_url
        self.scopes = settings.AZURE_SCOPES

    def _get_app(self) -> msal.ConfidentialClientApplication:
        """Get MSAL client application."""
        return msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
        )

    def get_authorization_url(self, state: str) -> str:
        """Get the authorization URL for Azure AD login."""
        app = self._get_app()
        return app.get_authorization_request_url(
            scopes=self.scopes,
            state=state,
            redirect_uri=self.redirect_uri,
        )

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for user profile.
        Raises ValueError on failure.
        """
        app = self._get_app()
        result = app.acquire_token_by_authorization_code(
            code=code,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )

        if "error" in result:
            raise ValueError(
                f"Azure AD token exchange failed: {result.get('error_description', result['error'])}"
            )

        claims = result.get("id_token_claims", {})
        if not claims.get("oid") or not claims.get("preferred_username"):
            raise ValueError("Azure AD response missing required user claims")

        return {
            "azure_object_id": claims["oid"],
            "email": claims.get("preferred_username") or claims.get("email"),
            "display_name": claims.get("name", claims.get("preferred_username", "Unknown User")),
            "tenant_id": claims.get("tid"),
        }

azure_auth = AzureAuthService()