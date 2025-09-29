import backtrader as bt
import pandas as pd
from sqlalchemy.orm import Session
from app.models.market_data import Price
from app.models.backtest import Backtest, Metric, BacktestStatus, Trade
from app.strategies.sma_cross import SMACross
from app.strategies.factory import get_strategy

def run_backtest(db: Session, backtest_params: dict):
    # Extrai os parâmetros do dicionário
    ticker = backtest_params['ticker']
    start_date_str = backtest_params['start_date']
    end_date_str = backtest_params['end_date']
    initial_cash = backtest_params['initial_cash']

    cerebro = bt.Cerebro()
    strategy_name = backtest_params['strategy_type']

    try:
        strategy_class = get_strategy(strategy_name)
    except ValueError as e:
        # Se a estratégia não for encontrada, retorna um erro claro
        return {"error": str(e)}
    
    strategy_params = backtest_params.get('strategy_params', {})
    if strategy_name == 'sma_cross_ml':
        strategy_params['ticker'] = ticker
    cerebro.addstrategy(strategy_class, **strategy_params)



    query = (
        db.query(Price.date, Price.open, Price.high, Price.low, Price.close, Price.volume)
        .filter(Price.symbol.has(ticker=ticker))
        .filter(Price.date.between(start_date_str, end_date_str))
        .order_by(Price.date)
    )
    
    df = pd.read_sql(query.statement, db.bind, index_col='date')
    df.index = pd.to_datetime(df.index)

    if df.empty:
        return {"error": "Não há dados históricos para este ticker no período solicitado."}

    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data_feed)
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', timeframe=bt.TimeFrame.Days, compression=1, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    print(f'Iniciando backtest com capital de R${initial_cash:.2f}')
    initial_portfolio_value = cerebro.broker.getvalue()
    
    results = cerebro.run()
    
    final_portfolio_value = cerebro.broker.getvalue()
    print(f'Backtest finalizado. Valor final do portfólio: R${final_portfolio_value:.2f}')

    strat = results[0]
    trade_analysis = strat.analyzers.trade_analyzer.get_analysis()
    sharpe_analysis = strat.analyzers.sharpe_ratio.get_analysis()
    drawdown_analysis = strat.analyzers.drawdown.get_analysis()

    sharpe_ratio = sharpe_analysis.get('sharperatio') if sharpe_analysis else 0.0
    max_drawdown = drawdown_analysis.get('max', {}).get('drawdown', 0.0)

    total_closed_trades = trade_analysis.get('total', {}).get('closed', 0)
    won_trades = trade_analysis.get('won', {}).get('total', 0)
    pnl_net_total = trade_analysis.get('pnl', {}).get('net', {}).get('total', 0.0)

    win_rate_percentage = (won_trades / total_closed_trades * 100) if total_closed_trades > 0 else 0.0

    metrics = {
        "total_return_percentage": ((final_portfolio_value - initial_portfolio_value) / initial_portfolio_value) * 100,
        "sharpe_ratio": sharpe_ratio if sharpe_ratio is not None else 0.0,
        "max_drawdown_percentage": max_drawdown,
        "total_closed_trades": total_closed_trades,
        "win_rate_percentage": win_rate_percentage,
        "total_net_pnl": pnl_net_total,
    }
    
    new_backtest = Backtest(
        ticker=ticker,
        start_date=start_date_str,
        end_date=end_date_str,
        initial_cash=initial_cash,
        strategy_type=backtest_params['strategy_type'],
        strategy_params_json=backtest_params.get('strategy_params'),
        status=BacktestStatus.COMPLETED
    )
    db.add(new_backtest)
    db.commit()
    db.refresh(new_backtest)

    if 'trades' in trade_analysis and trade_analysis.trades:
        for t in trade_analysis.trades:
            new_trade = Trade(
                backtest_id=new_backtest.id,
                size=t.size,
                price_entry=t.price,
                date_entry=t.open_datetime.date(),
                price_exit=t.close_price,
                date_exit=t.close_datetime.date(),
                pnl=t.pnl,
                pnl_comm=t.pnlcomm
            )
            db.add(new_trade)
        db.commit()
    

    new_metrics = Metric(
        backtest_id=new_backtest.id,
        total_return_percentage=metrics['total_return_percentage'],
        sharpe_ratio=metrics['sharpe_ratio'],
        max_drawdown_percentage=metrics['max_drawdown_percentage'],
        win_rate_percentage=metrics['win_rate_percentage'],
        total_net_pnl=metrics['total_net_pnl'],
        total_closed_trades=metrics['total_closed_trades']
    )
    db.add(new_metrics)
    db.commit()

    return {
        "backtest_id": new_backtest.id,
        "ticker": new_backtest.ticker,
        "initial_portfolio_value": initial_portfolio_value,
        "final_portfolio_value": final_portfolio_value,
        "metrics": metrics
    }