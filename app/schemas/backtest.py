# app/schemas/backtest.py
from pydantic import BaseModel
from typing import List, Optional
import datetime

class TradeSchema(BaseModel):
    size: float
    price_entry: float
    date_entry: datetime.date
    price_exit: float
    date_exit: datetime.date
    pnl: float

    class Config:
        from_attributes = True

class MetricSchema(BaseModel):
    total_return_percentage: float
    sharpe_ratio: Optional[float]
    max_drawdown_percentage: float
    win_rate_percentage: float

    class Config:
        from_attributes = True

class BacktestResultSchema(BaseModel):
    backtest_id: int
    ticker: str
    strategy_type: str
    metrics: MetricSchema
    trades: List[TradeSchema] = []