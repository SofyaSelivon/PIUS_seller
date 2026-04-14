from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.user import User


async def get_orders_with_stats(
    db: AsyncSession, market_id, status=None, page: int = 1, limit: int = 10
):

    query = (
        select(
            Order,
            func.count(OrderItem.id).label("items_count"),
            User.userId,
            User.firstName,
            User.lastName,
            User.patronymic,
            User.telegram,
        )
        .join(User, User.userId == Order.userId)
        .outerjoin(OrderItem, OrderItem.orderId == Order.id)
        .where(Order.marketId == market_id, Order.deletedAt.is_(None))
        .group_by(Order.id, User.userId)
    )

    if status:
        query = query.where(Order.status == status)

    total_orders = (
        await db.execute(
            select(func.count(Order.id)).where(
                Order.marketId == market_id, Order.deletedAt.is_(None)
            )
        )
    ).scalar()

    total_revenue = (
        await db.execute(
            select(func.coalesce(func.sum(Order.totalAmount), 0)).where(
                Order.marketId == market_id,
                Order.status != OrderStatus.cancelled,
                Order.deletedAt.is_(None),
            )
        )
    ).scalar()

    completed_orders = (
        await db.execute(
            select(func.count(Order.id)).where(
                Order.marketId == market_id,
                Order.status == OrderStatus.completed,
                Order.deletedAt.is_(None),
            )
        )
    ).scalar()

    processing_orders = (
        await db.execute(
            select(func.count(Order.id)).where(
                Order.marketId == market_id,
                Order.status.in_([OrderStatus.processing, OrderStatus.shipped]),
                Order.deletedAt.is_(None),
            )
        )
    ).scalar()

    pending_orders = (
        await db.execute(
            select(func.count(Order.id)).where(
                Order.marketId == market_id,
                Order.status == OrderStatus.pending,
                Order.deletedAt.is_(None),
            )
        )
    ).scalar()

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))

    rows = result.all()

    orders = []

    for order, items_count, uid, first, last, pat, telegram in rows:
        full_name = " ".join(filter(None, [first, last, pat]))

        orders.append(
            {
                "id": order.id,
                "orderNumber": order.orderNumber,
                "customer": {"id": uid, "fullName": full_name, "telegram": telegram},
                "deliveryAddress": order.deliveryAddress,
                "totalAmount": float(order.totalAmount),
                "itemsCount": items_count,
                "status": order.status,
                "createdAt": order.createdAt,
            }
        )

    return {
        "orders": orders,
        "statistics": {
            "totalOrders": total_orders,
            "totalRevenue": float(total_revenue),
            "completedOrders": completed_orders,
            "processingOrders": processing_orders,
            "pendingOrders": pending_orders,
        },
        "pagination": {"total": total_orders},
    }


async def update_order_status(db: AsyncSession, order: Order, new_status: OrderStatus):
    order.status = new_status
    await db.commit()
    return True


async def soft_delete_order(db: AsyncSession, order: Order):
    order.deletedAt = func.now()
    await db.commit()
    return True
