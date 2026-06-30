from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime
    details: Optional[Any] = None