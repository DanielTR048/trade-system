import backtrader as bt

class SMACross(bt.Strategy):
    # Parâmetros da estratégia que podem ser passados ao iniciar o backtest
    params = (
        ('fast_length', 10),
        ('slow_length', 50),
    )

    def __init__(self):
        """
        Este método é chamado uma vez no início, para configurar a estratégia.
        """
        # Obter a linha de dados de fechamento
        self.dataclose = self.datas[0].close

        # Criar as duas médias móveis
        self.fast_sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fast_length
        )
        self.slow_sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slow_length
        )

        # Criar um indicador de cruzamento entre as médias
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)

    def next(self):
        """
        Este método é chamado para cada barra (cada dia) no conjunto de dados.
        É aqui que a lógica de compra e venda acontece.
        """
        # Se já estivermos no mercado (comprados), não fazemos nada até o sinal de venda
        if self.position:
            # Se a média rápida cruzou para BAIXO da média lenta, é um sinal de VENDA
            if self.crossover < 0:
                print(f'SINAL DE VENDA: Fechando posição em {self.dataclose[0]:.2f}')
                self.close() # Vende a posição atual

        # Se não estivermos no mercado
        else:
            # Se a média rápida cruzou para CIMA da média lenta, é um sinal de COMPRA
            if self.crossover > 0:
                print(f'SINAL DE COMPRA: Comprando em {self.dataclose[0]:.2f}')
                self.buy() # Compra com o tamanho padrão