import os
import time

import dxlib as dx
from dxlib.interfaces.internal import MarketInterface
from dxlib.strategies.custom_strategies import RsiStrategy


def main():
    logger = dx.InfoLogger()
    interface_port = int(os.environ.get("INTERFACE_PORT", 8001))

    strategy = RsiStrategy(field="price")

    interface = MarketInterface(interface_url=f"http://localhost:{interface_port}")
    args = {
        "tickers": ["AAPL", "MSFT"],
        "start": "2024-02-01",
        "end": "2024-02-28",
    }

    executor = dx.Executor(strategy)

    try:
        while True:
            bars = interface.request(interface.quote, json=args)
            signals = executor.run(bars)
            print(signals)
            time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Strategy manager has been shutdown.")


if __name__ == "__main__":
    main()
