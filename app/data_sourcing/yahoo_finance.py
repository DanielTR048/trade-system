import yfinance as yf
import pandas as pd
# Não precisamos mais do 'requests' aqui

def fetch_ohlcv(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Busca dados históricos (OHLCV) de um ticker no Yahoo Finance.
    Deixa o yfinance gerenciar sua própria sessão de rede.
    """
    print(f"Buscando dados para {ticker} de {start_date} a {end_date}...")
    
    # Cria o objeto Ticker sem passar uma sessão.
    # A biblioteca vai criar e gerenciar a sessão correta (curl_cffi) internamente.
    ticker_obj = yf.Ticker(ticker)
    
    # Usa o método .history() para buscar os dados
    data = ticker_obj.history(start=start_date, end=end_date)
    
    if data.empty:
        print(f"Nenhum dado encontrado para {ticker}.")
        return pd.DataFrame()
        
    print(f"Dados de {ticker} baixados com sucesso.")
    return data