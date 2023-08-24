from datetime import datetime

import dxlib as dx
from dxlib.simulation import SimulationManager


def run_simulation(simulation_manager, starting_cash, data, logger):
    for _ in range(len(data)):
        with simulation_manager.server.exceptions as exceptions:
            if exceptions:
                logger.exception(exceptions)
                break

        step_signals = simulation_manager.execute(steps=1)

        if step_signals:
            returns = (simulation_manager.portfolio.current_value - starting_cash) / starting_cash
            logger.warning(f"Current returns {returns * 100:.2f}%")

        if simulation_manager.finished or simulation_manager.current_step >= len(data) - 5:
            break


def main():
    starting_cash = 1e4

    start = "2022-01-01"
    end = "2022-12-31"

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    interval = (end_date - start_date).days / 365.25

    portfolio = dx.Portfolio()
    portfolio.add_cash(starting_cash)
    strategy = StrategyManeira()

    data = dx.api.YFinanceAPI().get_historical_bars(["AAPL", "MSFT", "GOOGL", "AMZN"], start=start, end=end)

    market_api = dx.api()

    logger = dx.info_logger()
    executor_manager = ExecutionManager(portfolio, strategy, data["Close"], use_server=True, port=5000,
                                        logger=logger)

    executor_manager.start_server()

    try:
        while executor_manager.server.is_alive() and market_api.is_market_open:
            with executor_manager.server.exceptions as exceptions:
                if exceptions:
                    logger.exception(exceptions)
            executor_manager.read_market()
    except KeyboardInterrupt:
        pass
    finally:
        executor_manager.stop_server()


if __name__ == "__main__":
    main()
