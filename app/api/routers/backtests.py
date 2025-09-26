from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services import backtest_runner_service
from pydantic import BaseModel

router = APIRouter()

# Define o que esperamos receber no corpo do POST
class BacktestRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    initial_cash: float = 100000.0

@router.post("/run")
def run_new_backtest(
    request: BacktestRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Dispara um novo backtest.
    """
    try:
        results = backtest_runner_service.run_backtest(
            db=db,
            ticker=request.ticker,
            start_date_str=request.start_date,
            end_date_str=request.end_date,
            initial_cash=request.initial_cash
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))