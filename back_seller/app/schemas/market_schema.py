from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MarketResponse(BaseModel):
    market_id: UUID = Field(alias="marketId")
    market_name: str = Field(alias="marketName")
    description: Optional[str]
    created_at: datetime = Field(alias="createdAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class MarketUpdate(BaseModel):
    market_name: Optional[str] = None
    description: Optional[str] = None


class MarketCreate(BaseModel):
    marketName: str
    description: str | None = None
