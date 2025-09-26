from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, JSON, Enum as SQLAlchemyEnum
from .base import Base
import datetime
import enum

class BacktestStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Backtest(Base):
    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(Date, default=datetime.date.today)
    ticker = Column(String, index=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    strategy_type = Column(String, nullable=False)
    strategy_params_json = Column(JSON)
    initial_cash = Column(Float, default=100000.0)
    commission = Column(Float, default=0.0)
    status = Column(SQLAlchemyEnum(BacktestStatus), default=BacktestStatus.PENDING, nullable=False)