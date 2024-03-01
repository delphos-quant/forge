import os

import dxlib as dx
from dxlib.interfaces.internal import StrategyInterface, MarketInterface
from dxlib.strategies.custom_strategies import RsiStrategy


def main():
    logger = dx.InfoLogger()
    server_port = int(os.environ.get("STRATEGY_PORT", 8000))
    interface_port = int(os.environ.get("INTERFACE_PORT", 8001))

    strategy = RsiStrategy()

    interface = MarketInterface(interface_url=f"http://localhost:{interface_port}")
    args = {
        "tickers": ["AAPL", "MSFT"],
        "start": "2024-02-01",
        "end": "2024-02-28",
    }
    print(interface.request(interface.historical.endpoint, json=args))

    server = dx.HTTPServer(port=server_port, logger=logger)
    server.add_interface(interface)

    server.start()
    try:
        while server.alive:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        logger.info("Strategy manager has been shutdown.")


if __name__ == "__main__":
    main()
