import backtrader as bt
from .indicators import DonchianChannels

class Breakout(bt.Strategy):
    """
    Estratégia de Breakout (versão simplificada e corrigida).
    Compra quando o preço rompe a máxima dos últimos N períodos.
    Vende quando o preço rompe a mínima dos últimos N períodos.
    """
    params = (
        ('period', 20),
    )

    def __init__(self):
        # Apenas o indicador Donchian é necessário.
        self.donchian = DonchianChannels(self.datas[0], period=self.params.period)
        # O indicador 'crossover' foi removido por não ser utilizado.

    def next(self):
        # Aguarda o indicador ter dados suficientes para calcular (período de aquecimento)
        if len(self.data) < self.p.period:
            return

        # Lógica de compra
        if not self.position:
            # O preço fechou acima da máxima dos últimos 20 dias?
            if self.datas[0].close > self.donchian.dch[0]:
                self.buy() # Sinal de compra

        # Lógica de venda
        else:
            # O preço fechou abaixo da mínima dos últimos 20 dias?
            if self.datas[0].close < self.donchian.dcl[0]:
                self.close() # Sinal de venda