"""License models."""

from datetime import datetime

from pydantic import BaseModel


class License(BaseModel):
    """A Bible license."""

    id: int
    name: str
    version: int
    organization_id: str  # UUID
    html: str
    bible_ids: list[int] = []
    uri: str | None = None
    agreed_dt: datetime | None = None
    yvp_user_id: str
