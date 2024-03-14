import dxlib as dx
import pandas as pd

import plotly.express as px


def main():
    api = dx.interfaces.YFinanceAPI()
    historical = api.historical(["AAPL"], dx.Date.prevdays(365), dx.Date.today(), cache=True)

    # fill df na backfill
    historical.df = historical.df.fillna(method="bfill")

    executor = dx.Executor(dx.strategies.RsiStrategy(upper=70, lower=30, reverse=True))
    lo_executor = dx.Executor(dx.strategies.LongOnlyStrategy())
    signals = lo_executor.run(historical)

    portfolio = dx.Portfolio.from_orders(dx.OrderInterface().execute_history(signals))

    cash_value = dx.PortfolioMetrics.cash_value(portfolio, historical, fees={"fixed": 0, "percent": 0.00})

    starting_cash = 1e4
    # set starting_value to 1e4
    cash_value.history.df += starting_cash

    equity = dx.PortfolioMetrics.equity(portfolio, cash_value, historical)
    df = (equity.df - starting_cash) / starting_cash

    fig = px.line(df.reset_index(), x="date", y="value", title="Equity Curve")
    fig.update_yaxes(tickformat="%")

    inventory = portfolio.history.apply(lambda x: pd.Series(x['inventory'].securities), axis=1).df
    inventory.columns = [security.ticker for security in inventory.columns]

    fig2 = px.line(inventory.reset_index(),
                   x="date",
                   y=[column for column in inventory.columns],
                   title="Inventory")

    fig.show()
    fig2.show()


if __name__ == '__main__':
    main()
