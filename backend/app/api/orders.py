from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Order, OrderItem
from app.schemas.order import OrderDetail, OrderItemRead, OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderRead])
def list_orders(
    status: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Order]:
    query = db.query(Order).order_by(Order.order_time.desc())
    if status:
        query = query.filter(Order.status == status)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(Order.order_no.ilike(pattern) | Order.customer_name.ilike(pattern))
    return query.limit(200).all()


@router.get("/{order_id}", response_model=OrderDetail)
def get_order(order_id: int, db: Session = Depends(get_db)) -> OrderDetail:
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return OrderDetail(
        id=order.id,
        order_no=order.order_no,
        customer_name=order.customer_name,
        status=order.status,
        total_amount=order.total_amount,
        order_time=order.order_time,
        items=[
            OrderItemRead(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
            )
            for item in order.items
        ],
    )
