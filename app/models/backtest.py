from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, JSON, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
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

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), nullable=False)
    # Detalhes da operação
    size = Column(Float)
    price_entry = Column(Float)
    date_entry = Column(Date)
    price_exit = Column(Float)
    date_exit = Column(Date)
    pnl = Column(Float) # Profit and Loss (Lucro e Prejuízo)
    pnl_comm = Column(Float) # PnL incluindo comissões

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), unique=True, nullable=False)
    
    total_return_percentage = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown_percentage = Column(Float)
    win_rate_percentage = Column(Float)
    total_net_pnl = Column(Float)
    total_closed_trades = Column(Integer)