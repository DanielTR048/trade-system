from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from sqlalchemy import text
from app.api.routers import data, backtests, ml


app = FastAPI(
    title="Trading System API",
    description="API para backtesting de estratégias de trading.",
    version="0.1.0"
)

# Incluir o roteador na aplicação
app.include_router(data.router, prefix="/data", tags=["Market Data"]) 
app.include_router(backtests.router, prefix="/backtests", tags=["Backtests"])
app.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])

@app.get("/health", tags=["Health Check"])
def health_check(db: Session = Depends(get_db)):
    """
    Verifica o status do serviço e a conexão com o banco de dados.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "service_status": "ok",
        "database_status": db_status
    }

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API do Sistema de Trading!"}