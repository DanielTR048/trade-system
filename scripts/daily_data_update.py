import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# --- Configuração de Caminho ---
# Adiciona a raiz do projeto ao path do Python para que possamos importar os módulos do 'app'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
# -----------------------------

from app.models.market_data import Symbol, Price
from app.data_sourcing.yahoo_finance import fetch_ohlcv

def update_all_tickers():
    """
    Atualiza os dados de preços para todos os tickers cadastrados no banco de dados.
    """
    print("--- Iniciando rotina de atualização diária de preços ---")
    
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Usa a DATABASE_URL para se conectar via localhost, pois o script roda fora do container
    db_url_str = os.getenv("DATABASE_URL", "")
    if not db_url_str:
        raise ValueError("DATABASE_URL não encontrada no arquivo .env")
        
    # Ajusta a URL para conectar via localhost
    db_url = db_url_str.replace("@db:", "@localhost:")
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Busca todos os símbolos cadastrados
        symbols = db.query(Symbol).all()
        if not symbols:
            print("Nenhum símbolo encontrado no banco de dados para atualizar.")
            return

        print(f"Encontrados {len(symbols)} símbolos para atualizar.")
        
        today = date.today()
        
        for symbol in symbols:
            # 2. Encontra a última data de preço para o símbolo atual
            last_price_date_result = (
                db.query(func.max(Price.date))
                .filter(Price.symbol_id == symbol.id)
                .one_or_none()
            )
            
            start_date_to_fetch = date(2020, 1, 1) # Padrão
            if last_price_date_result and last_price_date_result[0]:
                start_date_to_fetch = last_price_date_result[0] + timedelta(days=1)

            if start_date_to_fetch >= today:
                print(f"Dados para {symbol.ticker} já estão atualizados. Pulando.")
                continue

            # 3. Busca os dados novos no Yahoo Finance
            new_price_data = fetch_ohlcv(symbol.ticker, start_date_to_fetch.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
            
            if not new_price_data.empty:
                # 4. Salva os novos dados no banco
                new_price_data.columns = new_price_data.columns.str.lower()
                
                for index, row in new_price_data.iterrows():
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
                print(f"  -> {len(new_price_data)} novos registros salvos para {symbol.ticker}.")
            else:
                print(f"  -> Nenhum dado novo encontrado para {symbol.ticker}.")
                
    finally:
        db.close()
        
    print("--- Rotina de atualização finalizada ---")


if __name__ == "__main__":
    update_all_tickers()