import pandas as pd

import dxlib as dx
from dxlib import StrategyManager

from strategy import WindsockTradingStrategy


def main():
    logger = dx.no_logger()
    strategy = WindsockTradingStrategy()

    symbols = pd.read_csv("Symbols.csv")
    print(symbols)

    historical_bars = dx.api.YFinanceAPI().get_historical_bars(symbols.sample(100).values.flatten(),)

    history = dx.History(historical_bars)

    manager = StrategyManager(strategy, logger=logger)
    portfolio = dx.Portfolio(name="windsock")

    starting_cash = 1_000_000
    portfolio.add_cash(starting_cash)
    manager.register_portfolio(portfolio)

    try:
        manager.run(history)
    except KeyboardInterrupt:
        pass
    finally:
        logger = dx.info_logger("Metrics")
        logger.info("Windsock Strategy finished.")
        position = portfolio.position

        # Calculate position using position (dict) and last history close prices (pd.Series)
        # if security is in position, sum to value:
        value = 0
        for security, quantity in position.items():
            value += quantity * history.df["Close", security].dropna().iloc[-1]

        logger.info(f"Portfolio value: {value}")
        logger.info(f"Portfolio cash: {portfolio.current_cash}")

        total_value = value + portfolio.current_cash

        annualized_return = (total_value / starting_cash) ** (1 / (len(history.df) / 252)) - 1

        logger.info(f"Returns: {starting_cash} -> {total_value} = {annualized_return:.2%}")


if __name__ == "__main__":
    main()
