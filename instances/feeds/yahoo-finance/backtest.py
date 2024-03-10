from datetime import datetime
from itertools import product

import dxlib as dx
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def to_str(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def main(graphs=False, **kwargs):
    start = to_str("2023-02-20")
    end = to_str("2024-02-20")

    tickers = ["PETR4.SA"]
    benchmark = ["^BVSP"]

    transaction_cost = 0.3
    starting_cash = 1e4

    strategy = dx.strategies.RsiStrategy(reverse=True, **kwargs)

    data = dx.YFinanceAPI().historical(tickers, start=start, end=end, cache=True)
    ibov = dx.YFinanceAPI().historical(benchmark, start=start, end=end, cache=True)
    df = data.df.droplevel("security")

    fig = make_subplots(rows=3, cols=1, specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": True}]])
    fig.update_xaxes(rangeslider_visible=False)
    fig.add_trace(
        go.Candlestick(x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="PETR4"),
        row=1, col=1, secondary_y=False)

    df = ibov.df.droplevel("security")
    fig.add_trace(
        go.Candlestick(x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="IBOV"),
        row=1, col=1, secondary_y=True)

    executor = dx.Executor(strategy)
    signals = executor.run(data)
    schema = signals.schema
    inventory_change = dx.InventoryHistory.stack(signals.df, schema)
    assets_owned = inventory_change.unstack().apply({dx.SchemaLevel.SECURITY: lambda x: x.cumsum()}, schema)

    x = assets_owned.df.index.get_level_values(0)
    y = assets_owned.df["quantity"].values.flatten()
    fig.add_trace(go.Scatter(x=x, y=y, name="Assets Owned"), row=2, col=1)

    price = data.df["close"]

    def value(row):
        cost = row["inventory"].value(price.loc[row.name[0]].to_dict())
        return pd.Series({
            "cash": -(cost + transaction_cost * abs(row["inventory"].quantities))
        })

    schema = dx.Schema(
        levels=[dx.SchemaLevel.DATE],
        fields=["cash"]
    )

    cash_change = inventory_change.apply(value, schema, axis=1)

    cash_value = cash_change.apply(lambda x: x.cumsum(), schema)
    inventory_value = assets_owned.apply_on(
        data, lambda x, y: pd.DataFrame(x["quantity"] * y["close"], columns=["cash"])).apply({dx.SchemaLevel.DATE: lambda x: x.sum()}, schema)
    portfolio_value = (starting_cash +
                       cash_value.df +
                       inventory_value.df)

    returns = portfolio_value.pct_change().fillna(0)
    benchmark = ibov.df["close"]
    benchmark_returns = benchmark.pct_change().fillna(0)

    returns = (1 + returns).cumprod()
    x = returns.index.get_level_values(0)
    y = returns.fillna(0).values.flatten()
    fig.add_trace(go.Scatter(x=x, y=y, name="Portfolio Value"), row=3, col=1)

    benchmark_returns = (1 + benchmark_returns).cumprod()
    x = benchmark_returns.index.get_level_values(0)
    y = benchmark_returns.values.flatten()
    fig.add_trace(go.Scatter(x=x, y=y, name="IBOV"), row=3, col=1, secondary_y=True)

    returns.index = returns.index.get_level_values(0)

    final_value = portfolio_value.iloc[-1].values[0]
    benchmark_return = (benchmark.iloc[-1] / benchmark.iloc[0]) ** (1 / (len(benchmark) / 252)) - 1
    annualized_return = (final_value / starting_cash) ** (1 / (len(returns) / 252)) - 1

    if graphs:
        fig.show()

    return annualized_return, benchmark_return


def optimize(grid):
    results = {}
    best_params = []
    best = [-np.Inf]

    for params in product(*grid.values()):
        kwargs = dict(zip(grid.keys(), params))
        results[params], _ = main(**kwargs)

        if results[params] > best[-1]:
            best_params.append(params)
            best.append(results[params])
            print(f"Best performance: {best[-1] * 100:.4f}%")

    return best_params[-1], best[-1]


if __name__ == "__main__":
    grid = {
        "window": [14, 21, 28, 50],
        "upper": [70, 75, 80],
        "lower": [30, 25, 20],
    }

    optimize(grid)
