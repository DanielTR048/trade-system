from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services import backtest_runner_service
from pydantic import BaseModel
from typing import Optional
from app.models.backtest import Backtest, Metric, Trade
from app.schemas.backtest import BacktestResultSchema

router = APIRouter()

# Define o que esperamos receber no corpo do POST
class BacktestRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    initial_cash: float = 100000.0
    strategy_type: str
    strategy_params: Optional[dict] = None



@router.post("/run")
def run_new_backtest(
    request: BacktestRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Dispara e salva um novo backtest.
    """
    try:
        # Converte o Pydantic model para um dicionário
        backtest_params = request.model_dump() 
        results = backtest_runner_service.run_backtest(
            db=db,
            backtest_params=backtest_params
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{backtest_id}/results", response_model=BacktestResultSchema)
def get_backtest_results(backtest_id: int, db: Session = Depends(deps.get_db)):
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest não encontrado.")

    metrics = db.query(Metric).filter(Metric.backtest_id == backtest_id).first()
    trades = db.query(Trade).filter(Trade.backtest_id == backtest_id).all()

    return BacktestResultSchema(
        backtest_id=backtest.id,
        ticker=backtest.ticker,
        strategy_type=backtest.strategy_type,
        metrics=metrics,
        trades=trades
    )

@router.get("/")
def list_backtests(db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100):
    """
    Lista todos os backtests executados com paginação.
    """
    backtests = db.query(Backtest).order_by(Backtest.id.desc()).offset(skip).limit(limit).all()
    return backtests