import backtrader as bt

class DonchianChannels(bt.Indicator):
    """
    Implementação do indicador Donchian Channels (versão corrigida).
    """
    alias = ('DCH', 'DonchianChannel',)

    lines = ('dch', 'dcm', 'dcl',)  # high, mid, low
    params = (
        ('period', 20),
        # O parâmetro 'lookback' foi removido daqui
    )

    plotinfo = dict(subplot=False)
    plotlines = dict(
        dcm=dict(ls='--'),
        dcl=dict(_samecolor=True),
        dch=dict(_samecolor=True),
    )

    def __init__(self):
        super().__init__()
        # O argumento 'lookback' também foi removido das chamadas abaixo
        self.l.dch = bt.indicators.Highest(self.data.high, period=self.p.period)
        self.l.dcl = bt.indicators.Lowest(self.data.low, period=self.p.period)
        
        self.l.dcm = (self.l.dch + self.l.dcl) / 2.0