from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Product
from app.schemas.common import MessageResponse
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate, StockAdjust

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(
    keyword: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Product]:
    query = db.query(Product).order_by(Product.id.asc())
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(Product.name.ilike(pattern), Product.category.ilike(pattern)))
    if category:
        query = query.filter(Product.category == category)
    return query.all()


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)) -> Product:
    product = get_product_or_404(db, product_id)
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    product = get_product_or_404(db, product_id)
    if product.items:
        product.status = "inactive"
        db.commit()
        return MessageResponse(message="商品已有订单记录，已改为下架状态")
    db.delete(product)
    db.commit()
    return MessageResponse(message="商品已删除")


@router.post("/{product_id}/stock", response_model=ProductRead)
def adjust_stock(product_id: int, payload: StockAdjust, db: Session = Depends(get_db)) -> Product:
    product = get_product_or_404(db, product_id)
    next_stock = product.current_stock + payload.delta
    if next_stock < 0:
        raise HTTPException(status_code=400, detail="库存不能小于 0")
    product.current_stock = next_stock
    db.commit()
    db.refresh(product)
    return product


def get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product
