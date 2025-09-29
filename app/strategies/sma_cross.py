import backtrader as bt
import math

class SMACross(bt.Strategy):
    params = (
        ('fast_length', 10),
        ('slow_length', 50),
        ('atr_period', 14), # Período para o cálculo do ATR
        ('risk_per_trade_percentage', 1.0), # Risco de 1% por operação
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.fast_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.fast_length)
        self.slow_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.slow_length)
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
        
        # Indicador de Volatilidade (Average True Range)
        self.atr = bt.indicators.AverageTrueRange(self.datas[0], period=self.params.atr_period)

    def next(self):
        # Lógica de fechamento de posição
        if self.position:
            if self.crossover < 0:
                print(f'SINAL DE VENDA (Cruzamento): Fechando posição em {self.dataclose[0]:.2f}')
                self.close()

        # Lógica de abertura de posição
        elif self.crossover > 0:
            # --- LÓGICA DE GESTÃO DE RISCO E POSITION SIZING ---

            # 1. Definir o preço do stop loss
            # Usaremos 2x o ATR abaixo do preço atual como nosso stop.
            stop_price = self.dataclose[0] - 2 * self.atr[0]

            # 2. Calcular o risco monetário por ação
            risk_per_share = self.dataclose[0] - stop_price
            if risk_per_share <= 0:
                return # Evita divisão por zero se o risco for nulo ou negativo

            # 3. Calcular quanto do nosso capital total podemos arriscar
            total_capital = self.broker.getvalue()
            risk_amount = (self.params.risk_per_trade_percentage / 100) * total_capital

            # 4. Calcular o tamanho da posição (quantas ações comprar)
            # Usamos math.floor para arredondar para baixo
            position_size = math.floor(risk_amount / risk_per_share)

            if position_size <= 0:
                return # Não abre a posição se o tamanho for 0

            print(f'SINAL DE COMPRA: {self.datas[0].datetime.date(0)}')
            print(f'  Preço: {self.dataclose[0]:.2f}, Tamanho: {position_size}, Stop: {stop_price:.2f}, Risco: R${risk_amount:.2f}')
            
            # Executa a ordem de compra com um stop loss atrelado (ordem Bracket)
            self.buy(size=position_size, exectype=bt.Order.Market, transmit=False)
            self.sell(price=stop_price, size=position_size, exectype=bt.Order.Stop, transmit=True)