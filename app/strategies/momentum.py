import backtrader as bt

class Momentum(bt.Strategy):
    """
    Estratégia de Momentum simples.
    Compra quando o momentum (medido pelo ROC) fica positivo.
    Vende quando o momentum fica negativo.
    """
    params = (
        ('period', 60), # Período de 60 dias para o cálculo do momentum
    )

    def __init__(self):
        # Rate of Change (Taxa de Variação) sobre 100 períodos.
        # Mede a variação percentual do preço ao longo do período.
        self.roc = bt.indicators.RateOfChange100(
            self.datas[0], period=self.p.period
        )

    def next(self):
        if not self.position:  # Se não estiver no mercado
            if self.roc[0] > 0: # Se o momentum dos últimos 60 dias for positivo
                self.buy()

        else:  # Se já estiver comprado
            if self.roc[0] < 0: # Se o momentum virou negativo
                self.close()