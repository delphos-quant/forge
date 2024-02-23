import dxlib as dx
from dxlib.strategies.custom_strategies import RsiStrategy
import pandas as pd
from plotly import express as px

strategy = RsiStrategy(upper=90, lower=10, window=500, reverse=True)


def main():
    security_manager = dx.SecurityManager.from_list(["AAPL"])
    aapl = security_manager.get("AAPL")

    scheme = dx.HistorySchema(
        levels=[dx.HistoryLevel.DATE, dx.HistoryLevel.SECURITY],
        fields=["close"],
        security_manager=security_manager,
    )

    df = pd.read_csv("data_file.csv")
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.index = pd.MultiIndex.from_tuples([(date, aapl) for date in df.index])

    history = dx.History(df, scheme)
    signals: dx.History = dx.Executor(strategy, input_scheme=scheme).run(history, in_place=True)

    data = pd.Series({date: dx.OrderData.from_signal(signal, aapl) for date, signal in signals.df["signal"].items()})

    prices = history.df["close"]
    traded = pd.Series({date: (order.quantity or 0) * order.side.value for date, order in data.items()})
    shares = traded.cumsum()
    returns = prices.pct_change().shift(-1).fillna(0)
    value = ((shares * returns).cumsum() * prices[0]).reset_index()[0]
    shares = shares.reset_index()[0]

    # line 1: portfolio value in R$ (value)
    # line 2: position in shares (shares)
    fig = px.line(value, title="Portfolio Value")
    fig.add_scatter(x=shares.index, y=shares.values, name="Position", yaxis="y2")

    fig.show()


if __name__ == "__main__":
    main()
