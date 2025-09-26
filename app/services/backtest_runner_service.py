import backtrader as bt
import pandas as pd
from sqlalchemy.orm import Session
from app.models.market_data import Price
from app.strategies.sma_cross import SMACross # Importa nossa estratégia

def run_backtest(db: Session, ticker: str, start_date_str: str, end_date_str: str, initial_cash: float):
    # 1. Criar uma instância do Cerebro (o motor do backtrader)
    cerebro = bt.Cerebro()

    # 2. Adicionar a estratégia ao Cerebro
    cerebro.addstrategy(SMACross) # Por enquanto, fixo na SMACross

    # 3. Buscar os dados do NOSSO banco de dados
    query = (
        db.query(Price.date, Price.open, Price.high, Price.low, Price.close, Price.volume)
        .filter(Price.symbol.has(ticker=ticker))
        .filter(Price.date.between(start_date_str, end_date_str))
        .order_by(Price.date)
    )
    
    # Converter os dados para um DataFrame do Pandas, que o backtrader entende
    df = pd.read_sql(query.statement, db.bind, index_col='date')

    # Se não houver dados, retorne um erro
    if df.empty:
        return {"error": "Não há dados históricos para este ticker no período solicitado."}

    # 4. Criar o Data Feed para o backtrader
    data_feed = bt.feeds.PandasData(dataname=df)

    # 5. Adicionar os dados ao Cerebro
    cerebro.adddata(data_feed)

    # 6. Configurar o capital inicial
    cerebro.broker.setcash(initial_cash)
    
    # 7. Configurar comissão (ex: 0.1% por operação)
    cerebro.broker.setcommission(commission=0.001)

    # 8. Rodar o backtest!
    print(f'Iniciando backtest com capital de R${initial_cash:.2f}')
    initial_portfolio_value = cerebro.broker.getvalue()
    
    results = cerebro.run()
    
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Backtest finalizado. Valor final do portfólio: R${final_portfolio_value:.2f}')

    # 9. Retornar os resultados
    return {
        "ticker": ticker,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "initial_portfolio_value": initial_portfolio_value,
        "final_portfolio_value": final_portfolio_value,
        "return_percentage": ((final_portfolio_value - initial_portfolio_value) / initial_portfolio_value) * 100
    }