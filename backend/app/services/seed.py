from __future__ import annotations

import random
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import (
    AnalysisRun,
    CategorySales,
    DailySales,
    InventoryAlert,
    Order,
    OrderItem,
    Product,
    ProductSales,
)

PRODUCT_CATALOG = [
    ("无线蓝牙耳机", "数码配件", Decimal("199.00"), 280, 60),
    ("机械键盘", "电脑办公", Decimal("369.00"), 140, 30),
    ("人体工学椅", "家居生活", Decimal("899.00"), 36, 15),
    ("智能手表", "智能设备", Decimal("699.00"), 95, 25),
    ("移动固态硬盘", "电脑办公", Decimal("529.00"), 72, 20),
    ("保温杯", "家居生活", Decimal("89.00"), 220, 50),
    ("筋膜枪", "运动健康", Decimal("299.00"), 65, 18),
    ("空气炸锅", "家用电器", Decimal("459.00"), 54, 16),
    ("路由器 AX3000", "智能设备", Decimal("329.00"), 88, 22),
    ("运动手环", "运动健康", Decimal("159.00"), 170, 40),
    ("显示器支架", "电脑办公", Decimal("149.00"), 130, 35),
    ("电动牙刷", "家居生活", Decimal("189.00"), 115, 30),
]

CUSTOMERS = [
    "张明",
    "李佳",
    "王磊",
    "赵欣",
    "陈晨",
    "刘洋",
    "周雨",
    "孙宁",
    "郑可",
    "吴昊",
]


def reset_demo_data(db: Session, order_count: int = 180) -> dict[str, int]:
    for model in (
        AnalysisRun,
        InventoryAlert,
        CategorySales,
        ProductSales,
        DailySales,
        OrderItem,
        Order,
        Product,
    ):
        db.execute(delete(model))
    db.commit()

    products = [
        Product(
            name=name,
            category=category,
            price=price,
            current_stock=stock,
            safety_stock=safety,
            status="active",
        )
        for name, category, price, stock, safety in PRODUCT_CATALOG
    ]
    db.add_all(products)
    db.flush()

    now = datetime.utcnow().replace(microsecond=0)
    random.seed(20260525)

    for index in range(order_count):
        order_time = now - timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        order = Order(
            order_no=f"EC{order_time.strftime('%Y%m%d')}{index + 1:05d}",
            customer_name=random.choice(CUSTOMERS),
            status=random.choices(["paid", "shipped", "completed", "cancelled"], [32, 36, 28, 4])[0],
            total_amount=Decimal("0.00"),
            order_time=order_time,
        )
        db.add(order)
        db.flush()

        line_total = Decimal("0.00")
        for product in random.sample(products, random.randint(1, 4)):
            quantity = random.randint(1, 5)
            unit_price = product.price
            item_total = unit_price * quantity
            line_total += item_total

            if order.status != "cancelled":
                product.current_stock = max(0, product.current_stock - quantity)

            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=item_total,
                )
            )

        order.total_amount = line_total if order.status != "cancelled" else Decimal("0.00")

    db.commit()
    return {"products": len(products), "orders": order_count}
