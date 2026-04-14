import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import Enum as SQLEnum

from app.database.base import Base


class OrderStatus(PyEnum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    completed = "completed"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    marketId = Column(UUID(as_uuid=True), ForeignKey("markets.marketId"), nullable=False)
    userId = Column(UUID(as_uuid=True), ForeignKey("users.userId"), nullable=False)
    orderNumber = Column(String, nullable=False)
    deliveryAddress = Column(String)
    totalAmount = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(OrderStatus, name="order_status"), default=OrderStatus.pending)
    deletedAt = Column(DateTime(timezone=True), nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
