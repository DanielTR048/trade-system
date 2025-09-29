import pandas as pd
import pandas_ta as ta
from sqlalchemy.orm import Session
from sklearn.linear_model import LogisticRegression
import joblib
import os

from app.models.market_data import Price

# Garante que o diretório para salvar os modelos exista
MODEL_DIR = "ml_models"
os.makedirs(MODEL_DIR, exist_ok=True)

def create_features_and_target(df: pd.DataFrame) -> pd.DataFrame:
    """Cria features de análise técnica e a variável alvo."""
    
    # Anexa os indicadores diretamente ao DataFrame usando o acessor .ta
    df.ta.sma(length=10, append=True)
    df.ta.sma(length=50, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.bbands(length=20, append=True) # Isso adicionará a coluna BBP_20_2.0

    print("COLUNAS DISPONÍVEIS APÓS BBANDS:", df.columns)
    
    # Agora criamos as colunas de feature a partir dos indicadores anexados
    df['sma_diff'] = df['SMA_10'] - df['SMA_50']
    df['volatility'] = df['BBP_20_2.0_2.0'] # Agora esta coluna existe
    df['rsi'] = df['RSI_14']
    
    # Retornos passados (lags)
    for lag in range(1, 6):
        df[f'return_lag_{lag}'] = df['close'].pct_change(lag)
        
    # Variável Alvo (Target)
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    
    df.dropna(inplace=True)
    
    return df

def train_model_for_ticker(db: Session, ticker: str):
    """Busca dados, cria features, treina e salva um modelo para um ticker."""
    print(f"Iniciando treinamento do modelo para {ticker}...")
    
    # 1. Busca todos os dados históricos do banco
    query = (
        db.query(Price.date, Price.open, Price.high, Price.low, Price.close, Price.volume)
        .filter(Price.symbol.has(ticker=ticker))
        .order_by(Price.date)
    )
    df = pd.read_sql(query.statement, db.bind, index_col='date')
    if df.empty or len(df) < 100: # Precisa de dados suficientes
        return {"error": "Dados insuficientes para treinamento."}

    # 2. Cria features e a variável alvo
    df_processed = create_features_and_target(df)
    
    feature_names = ['sma_diff', 'rsi', 'volatility', 'return_lag_1', 'return_lag_2', 'return_lag_3', 'return_lag_4', 'return_lag_5']
    X = df_processed[feature_names]
    y = df_processed['target']
    
    # 3. Treina o modelo de Regressão Logística
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    
    # 4. Salva o modelo treinado em um arquivo
    model_path = os.path.join(MODEL_DIR, f"model_{ticker}.joblib")
    joblib.dump(model, model_path)
    
    print(f"Modelo para {ticker} treinado e salvo em {model_path}")
    return {"message": "Modelo treinado com sucesso", "model_path": model_path}