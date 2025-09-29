import backtrader as bt

class TradeListAnalyzer(bt.Analyzer):
    """
    Um Analyzer que coleta todos os trades fechados em uma lista de dicionários.
    """
    def __init__(self):
        self.trades = []

    def notify_trade(self, trade):
        if trade.isclosed:
            self.trades.append({
                'size': trade.size,
                'price_entry': trade.price,          # Preço de entrada
                'date_entry': trade.open_datetime(),
                'price_exit': trade.value / trade.size if trade.size != 0 else 0, # Preço de saída calculado
                'date_exit': trade.close_datetime(),
                'pnl': trade.pnl,                    
                'pnl_comm': trade.pnlcomm           
            })

    def get_analysis(self):
        return self.trades