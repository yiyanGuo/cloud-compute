from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AnalysisRun
from app.schemas.analysis import AnalysisRunRead
from app.schemas.common import MessageResponse
from app.services.analysis import run_spark_analysis
from app.services.seed import reset_demo_data

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/seed", response_model=MessageResponse)
def seed_demo_data(db: Session = Depends(get_db)) -> MessageResponse:
    result = reset_demo_data(db)
    return MessageResponse(message=f"已初始化 {result['products']} 个商品和 {result['orders']} 个订单")


@router.post("/run", response_model=AnalysisRunRead)
def run_analysis(db: Session = Depends(get_db)) -> AnalysisRun:
    return run_spark_analysis(db)


@router.get("/runs", response_model=list[AnalysisRunRead])
def list_runs(db: Session = Depends(get_db)) -> list[AnalysisRun]:
    return db.query(AnalysisRun).order_by(desc(AnalysisRun.started_at)).limit(20).all()
