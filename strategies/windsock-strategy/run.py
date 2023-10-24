import pandas as pd

import dxlib as dx
from dxlib import StrategyManager

from strategy import WindsockTradingStrategy


def main():
    logger = dx.info_logger()
    strategy = WindsockTradingStrategy()

    symbols = pd.read_csv("Symbols.csv")
    print(symbols)

    historical_bars = dx.api.YFinanceAPI().get_historical_bars(symbols.head(100).values.flatten(),)

    history = dx.History(historical_bars)

    manager = StrategyManager(strategy, logger=logger)
    portfolio = dx.Portfolio(name="windsock")
    portfolio.add_cash(100_000)
    manager.register_portfolio(portfolio)

    try:
        manager.run(history)
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Windsock Strategy finished.")
        logger.info(f"Portfolio value: {portfolio.position}")
        logger.info(f"Portfolio cash: {portfolio.current_cash}")


if __name__ == "__main__":
    main()
