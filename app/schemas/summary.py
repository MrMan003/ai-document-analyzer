from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    executive_summary: str
    key_points: List[str] = []
    summary_type: str = "EXECUTIVE"
    created_at: datetime
    updated_at: datetime