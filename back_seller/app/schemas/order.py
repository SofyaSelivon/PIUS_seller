from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.order import OrderStatus


class CustomerOut(BaseModel):
    id: UUID
    fullName: str
    telegram: Optional[str]


class OrderOut(BaseModel):
    id: UUID
    orderNumber: str
    customer: CustomerOut
    deliveryAddress: Optional[str]
    totalAmount: float
    itemsCount: int
    status: OrderStatus
    createdAt: datetime


class StatisticsOut(BaseModel):
    totalOrders: int
    totalRevenue: float
    completedOrders: int
    processingOrders: int
    pendingOrders: int


class PaginatedOrdersOut(BaseModel):
    statistics: StatisticsOut
    orders: List[OrderOut]
    pagination: dict


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class SuccessResponse(BaseModel):
    success: bool
