import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.base import Base
from app.enums.product_category import ProductCategory


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    marketId = Column(UUID(as_uuid=True), ForeignKey("markets.marketId"), nullable=False)

    name = Column(String, nullable=False)

    description = Column(String)

    category = Column(Enum(ProductCategory, name="productcategory"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    img = Column(String)

    available = Column(Integer, nullable=False)

    createdAt = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_product_market", "marketId"),
        Index("idx_product_category", "category"),
        CheckConstraint("available >= 0", name="check_available_positive"),
    )
