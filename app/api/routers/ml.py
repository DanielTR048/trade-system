from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.ml import prediction_pipeline

router = APIRouter()

@router.post("/train/{ticker}", status_code=200)
def train_ticker_model(
    ticker: str,
    db: Session = Depends(deps.get_db)
):
    """
    Dispara o treinamento de um modelo de ML para um ticker específico.
    """
    try:
        result = prediction_pipeline.train_model_for_ticker(db=db, ticker=ticker)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))