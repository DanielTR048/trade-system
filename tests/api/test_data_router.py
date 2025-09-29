# tests/api/test_data_router.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime

from app.main import app
from app.api.deps import get_db
from tests.test_database import override_get_db, engine, TestingSessionLocal
from app.models.base import Base
from app.models.market_data import Symbol, Price

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_update_data_for_ticker(db_session: Session, mocker):
    """
    Testa o endpoint de atualização de dados usando um mock para o yfinance.
    """
    ticker = "VALE3.SA"

    mock_data = pd.DataFrame({
        'Open': [100.0, 102.0], 'High': [103.0, 104.0],
        'Low': [99.0, 101.0], 'Close': [102.0, 103.0],
        'Volume': [1000, 1200]
    }, index=pd.to_datetime([datetime(2024, 1, 1), datetime(2024, 1, 2)]))

    mocker.patch(
        'app.services.market_data_service.yahoo_finance.fetch_ohlcv', 
        return_value=mock_data
    )

    response = client.post(f"/data/update/{ticker}?start_date=2024-01-01&end_date=2024-01-10")

    assert response.status_code == 201
    assert "Dados para VALE3.SA atualizados com sucesso" in response.json()["message"]
    
    symbol_in_db = db_session.query(Symbol).filter(Symbol.ticker == ticker).first()
    assert symbol_in_db is not None
    
    prices_in_db = db_session.query(Price).filter(Price.symbol_id == symbol_in_db.id).all()
    assert len(prices_in_db) == 2
    assert prices_in_db[0].close == 102.0