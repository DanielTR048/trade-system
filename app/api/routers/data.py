from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services import market_data_service

router = APIRouter()

@router.post("/update/{ticker}", status_code=201)
def update_data_for_ticker(
    ticker: str,
    start_date: str = "2020-01-01",
    end_date: str = "2024-12-31",
    db: Session = Depends(deps.get_db)
):
    """
    Força a atualização/cálculo de indicadores para um ticker.
    Busca os dados do Yahoo Finance e salva no banco de dados.
    """
    try:
        result = market_data_service.update_symbol_data(
            db=db, 
            ticker=ticker.upper(), 
            start_date=start_date, 
            end_date=end_date
        )
        return result
    except Exception as e:
        # Em um app real, logaríamos o erro aqui
        raise HTTPException(
            status_code=500, 
            detail=f"Ocorreu um erro interno: {e}"
        )