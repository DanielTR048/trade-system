import backtrader as bt
import joblib
import os
import pandas as pd

from .sma_cross import SMACross

MODEL_DIR = "ml_models"

class SMACrossML(SMACross):
    params = (
        ('ticker', None),
    )

    def __init__(self):
        super().__init__()
        
        # Carrega o modelo de ML
        if not self.p.ticker:
            raise ValueError("Ticker deve ser fornecido para a estratégia de ML")
        
        model_path = os.path.join(MODEL_DIR, f"model_{self.p.ticker}.joblib")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo não encontrado em {model_path}. Treine o modelo primeiro.")
            
        self.model = joblib.load(model_path)
        print(f"Modelo de ML para {self.p.ticker} carregado com sucesso.")

        # --- RECRIA AS MESMAS FEATURES COM INDICADORES NATIVOS DO BACKTRADER (VERSÃO CORRIGIDA) ---
        sma1 = bt.indicators.SimpleMovingAverage(self.data.close, period=10)
        sma2 = bt.indicators.SimpleMovingAverage(self.data.close, period=50)
        self.sma_diff = sma1 - sma2
        
        self.rsi = bt.indicators.RSI(self.data.close, period=14)
        
        bollinger = bt.indicators.BollingerBands(self.data.close, period=20)
        # Garante que não haverá divisão por zero se as bandas forem iguais
        band_width = bollinger.lines.top - bollinger.lines.bot
        self.volatility = (self.data.close - bollinger.lines.bot) / band_width
        
        self.returns = [bt.indicators.PercentChange(self.data.close, period=i) for i in range(1, 6)]

    def next(self):
        original_buy_signal = not self.position and self.crossover > 0
        
        if original_buy_signal:
            try:
                # Coleta os valores atuais das features
                current_features = [
                    self.sma_diff[0],
                    self.rsi[0],
                    self.volatility[0],
                    self.returns[0][0],
                    self.returns[1][0],
                    self.returns[2][0],
                    self.returns[3][0],
                    self.returns[4][0]
                ]
                
                features_df = pd.DataFrame([current_features])
                prediction = self.model.predict(features_df)[0]
                
                if prediction == 1:
                    super().next() # Executa a compra
                else:
                    print(f"Sinal de compra em {self.datas[0].datetime.date(0)} IGNORADO pelo filtro de ML.")
            except IndexError:
                # Ocorre se os indicadores ainda não tiverem valores (período de aquecimento)
                pass
        else:
            # Para sinais de venda, usamos a lógica original sem filtro
            super().next()