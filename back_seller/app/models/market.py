import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.base import Base


class Market(Base):
    __tablename__ = "markets"

    marketId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"), nullable=False)

    marketName = Column(String, nullable=False)

    description = Column(String)

    createdAt = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("idx_market_user", "userId"),)
