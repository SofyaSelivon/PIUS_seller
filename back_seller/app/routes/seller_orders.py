from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import order as crud_order
from app.database.session import get_db
from app.models.market import Market
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.schemas.order import OrderStatusUpdate, PaginatedOrdersOut, SuccessResponse
from app.security.jwt_dependency import get_current_user

router = APIRouter(prefix="/api/v1/seller/orders", tags=["seller"])


@router.get("", response_model=PaginatedOrdersOut)
async def list_orders(
    page: int = Query(1),
    limit: int = Query(10),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Market.marketId).where(Market.userId == current_user["userId"])
    )
    market_id = result.scalar()

    if not market_id:
        return {
            "statistics": {
                "totalOrders": 0,
                "totalRevenue": 0,
                "completedOrders": 0,
                "processingOrders": 0,
                "pendingOrders": 0,
            },
            "orders": [],
            "pagination": {"page": page, "limit": limit, "totalItems": 0, "totalPages": 0},
        }

    return await crud_order.get_orders_with_stats(db, market_id, status, page, limit)


@router.get("/revenue")
async def get_revenue(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(Market.marketId).where(Market.userId == current_user["userId"])
    )
    market_id = result.scalar()

    if not market_id:
        return []

    start_date = datetime.utcnow() - timedelta(days=7)

    result = await db.execute(
        select(
            func.date(Order.createdAt).label("date"), func.sum(Order.totalAmount).label("revenue")
        )
        .where(
            Order.marketId == market_id, Order.deletedAt.is_(None), Order.createdAt >= start_date
        )
        .group_by(func.date(Order.createdAt))
        .order_by(func.date(Order.createdAt))
    )

    rows = result.all()

    return [{"date": str(row.date), "revenue": float(row.revenue or 0)} for row in rows]


@router.get("/revenue/total")
async def get_total_revenue(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(Market.marketId).where(Market.userId == current_user["userId"])
    )
    market_id = result.scalar()

    if not market_id:
        return {"totalRevenue": 0}

    result = await db.execute(
        select(func.sum(Order.totalAmount)).where(
            Order.marketId == market_id, Order.deletedAt.is_(None)
        )
    )

    total = result.scalar() or 0

    return {"totalRevenue": float(total)}


@router.get("/completed")
async def get_completed_orders(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(Market.marketId).where(Market.userId == current_user["userId"])
    )
    market_id = result.scalar()

    if not market_id:
        return {"completedOrders": 0}

    result = await db.execute(
        select(func.count(Order.id)).where(
            Order.marketId == market_id,
            Order.status == OrderStatus.completed,
            Order.deletedAt.is_(None),
        )
    )

    count = result.scalar() or 0

    return {"completedOrders": count}


@router.patch("/{order_id}/status", response_model=SuccessResponse)
async def update_status(
    order_id: UUID = Path(...),
    status_update: OrderStatusUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if status_update is None:
        raise HTTPException(400, "Status body is required")

    result = await db.execute(
        select(Market.marketId).where(Market.userId == current_user["userId"])
    )
    market_id = result.scalar()

    result = await db.execute(
        select(Order).where(
            Order.id == order_id, Order.marketId == market_id, Order.deletedAt.is_(None)
        )
    )
    order = result.scalar()

    if not order:
        raise HTTPException(404, "Order not found")

    allowed_transitions = {
        OrderStatus.pending: [OrderStatus.processing, OrderStatus.cancelled],
        OrderStatus.processing: [OrderStatus.shipped, OrderStatus.cancelled],
        OrderStatus.shipped: [OrderStatus.completed],
        OrderStatus.completed: [],
        OrderStatus.cancelled: [],
    }

    if status_update.status not in allowed_transitions[order.status]:
        raise HTTPException(400, "Invalid status transition")

    await crud_order.update_order_status(db, order, status_update.status)

    return {"success": True}


@router.delete("/{order_id}", response_model=SuccessResponse)
async def delete_order(
    order_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Market.marketId).where(Market.userId == current_user["userId"])
    )
    market_id = result.scalar()

    result = await db.execute(
        select(Order).where(
            Order.id == order_id, Order.marketId == market_id, Order.deletedAt.is_(None)
        )
    )
    order = result.scalar()

    if not order:
        raise HTTPException(404, "Order not found")

    await crud_order.soft_delete_order(db, order)

    return {"success": True}


@router.get("/{order_id}")
async def get_order_by_id(
    order_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Market.marketId).where(Market.userId == current_user["userId"])
    )
    market_id = result.scalar()

    result = await db.execute(
        select(Order).where(
            Order.id == order_id, Order.marketId == market_id, Order.deletedAt.is_(None)
        )
    )
    order = result.scalar()

    if not order:
        raise HTTPException(404, "Order not found")

    result = await db.execute(select(OrderItem).where(OrderItem.orderId == order.id))
    items = result.scalars().all()

    return {
        "id": order.id,
        "orderNumber": order.orderNumber,
        "deliveryAddress": order.deliveryAddress,
        "totalAmount": float(order.totalAmount),
        "status": order.status,
        "createdAt": order.createdAt,
        "items": [
            {"productId": item.productId, "quantity": item.quantity, "price": float(item.price)}
            for item in items
        ],
    }
