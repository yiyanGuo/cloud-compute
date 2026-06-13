from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SummaryMetric(BaseModel):
    total_sales: Decimal
    order_count: int
    product_count: int
    inventory_alert_count: int


class DailySalesPoint(BaseModel):
    sales_date: datetime
    order_count: int
    item_count: int
    sales_amount: Decimal


class ProductSalesPoint(BaseModel):
    product_id: int
    product_name: str
    category: str
    quantity_sold: int
    sales_amount: Decimal
    rank_no: int


class CategorySalesPoint(BaseModel):
    category: str
    quantity_sold: int
    sales_amount: Decimal


class InventoryAlertPoint(BaseModel):
    product_id: int
    product_name: str
    category: str
    current_stock: int
    safety_stock: int
    alert_level: str


class DashboardData(BaseModel):
    summary: SummaryMetric
    daily_sales: list[DailySalesPoint]
    product_sales: list[ProductSalesPoint]
    category_sales: list[CategorySalesPoint]
    inventory_alerts: list[InventoryAlertPoint]
    last_analysis_at: datetime | None
