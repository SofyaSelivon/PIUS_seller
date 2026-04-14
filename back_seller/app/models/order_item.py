import uuid

from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    orderId = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    productId = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
