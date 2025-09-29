from sqlalchemy.orm import Session
from app.data_sourcing import yahoo_finance
from app.models.market_data import Symbol, Price

def update_symbol_data(db: Session, ticker: str, start_date: str, end_date: str):
    price_data = yahoo_finance.fetch_ohlcv(ticker, start_date, end_date)
    
    if price_data.empty:
        return {"message": "Nenhum dado encontrado para atualizar."}
    
    # Padroniza nomes de colunas para minúsculas
    price_data.columns = [col.lower() for col in price_data.columns]
    
    try:
        symbol = db.query(Symbol).filter(Symbol.ticker == ticker).first()
        if not symbol:
            symbol = Symbol(ticker=ticker, name=ticker)
            db.add(symbol)
            db.commit()
            db.refresh(symbol)

        for index, row in price_data.iterrows():
            price_record = Price(
                symbol_id=symbol.id,
                date=index.date(),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=int(row['volume'])
            )
            db.add(price_record)

        db.commit()
        
        return {"message": f"Dados para {ticker} atualizados com sucesso."}

    except Exception as e:
        db.rollback()
        raise e