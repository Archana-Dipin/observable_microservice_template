from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

"""Pydantic schemas for API requests and responses."""

class HealthResponse(BaseModel):
    status : str
    service: str
    version: str

class ItemStatus(str,Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str
    status: ItemStatus

class Item(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    status: ItemStatus
    created_at:  datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

