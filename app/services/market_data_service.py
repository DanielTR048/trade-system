from sqlalchemy.orm import Session
from app.data_sourcing import yahoo_finance
from app.models.market_data import Symbol, Price


def update_symbol_data(db: Session, ticker: str, start_date: str, end_date: str):
    # 1. Buscar dados usando a função do passo 1
    price_data = yahoo_finance.fetch_ohlcv(ticker, start_date, end_date)
    
    if price_data.empty:
        return {"message": "Nenhum dado encontrado para atualizar."}
    
    price_data.columns = price_data.columns.str.lower()
        
    # 2. Verificar se o símbolo (ticker) existe no banco, se não, criar
    symbol = db.query(Symbol).filter(Symbol.ticker == ticker).first()
    if not symbol:
        symbol = Symbol(ticker=ticker, name=ticker) # Pode adicionar mais detalhes depois
        db.add(symbol)
        db.commit()
        db.refresh(symbol)
        
    # 3. Iterar sobre os dados do DataFrame e salvar no banco
    
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