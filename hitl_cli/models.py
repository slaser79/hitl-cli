from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, field_validator


class FileAttachment(BaseModel):
    download_url: HttpUrl
    filename: str
    content_type: str
    expires_at: datetime
    file_size: Optional[int] = None


class HumanResponse(BaseModel):
    # Backward compatible and future-proof structure
    text: str = ""
    approved: Optional[bool] = None
    attachments: List[FileAttachment] = []

    @field_validator("attachments", mode="before")
    @classmethod
    def _normalize_attachments(cls, v):
        # Accept None, single object, or list
        if v is None:
            return []
        if isinstance(v, dict):
            return [v]
        return v or []
