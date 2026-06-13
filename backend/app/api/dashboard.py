from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.models import (
    AnalysisRun,
    CategorySales,
    DailySales,
    InventoryAlert,
    Order,
    Product,
    ProductSales,
)
from app.schemas.dashboard import (
    CategorySalesPoint,
    DailySalesPoint,
    DashboardData,
    InventoryAlertPoint,
    ProductSalesPoint,
    SummaryMetric,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardData)
def dashboard(db: Session = Depends(get_db)) -> DashboardData:
    total_sales = db.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar()
    order_count = db.query(func.count(Order.id)).scalar()
    product_count = db.query(func.count(Product.id)).scalar()
    inventory_alert_count = db.query(func.count(InventoryAlert.id)).scalar()
    last_run = (
        db.query(AnalysisRun)
        .filter(AnalysisRun.status == "success")
        .order_by(desc(AnalysisRun.finished_at))
        .first()
    )

    daily_sales = db.query(DailySales).order_by(DailySales.sales_date.asc()).all()
    product_sales = db.query(ProductSales).order_by(ProductSales.rank_no.asc()).limit(10).all()
    category_sales = db.query(CategorySales).order_by(desc(CategorySales.sales_amount)).all()
    inventory_alerts = db.query(InventoryAlert).order_by(InventoryAlert.alert_level.desc()).all()

    return DashboardData(
        summary=SummaryMetric(
            total_sales=total_sales,
            order_count=order_count,
            product_count=product_count,
            inventory_alert_count=inventory_alert_count,
        ),
        daily_sales=[DailySalesPoint.model_validate(row, from_attributes=True) for row in daily_sales],
        product_sales=[ProductSalesPoint.model_validate(row, from_attributes=True) for row in product_sales],
        category_sales=[CategorySalesPoint.model_validate(row, from_attributes=True) for row in category_sales],
        inventory_alerts=[InventoryAlertPoint.model_validate(row, from_attributes=True) for row in inventory_alerts],
        last_analysis_at=last_run.finished_at if last_run else None,
    )
