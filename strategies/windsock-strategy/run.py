import os

import dxlib as dx
from dxlib import StrategyManager

from strategy import WindsockTradingStrategy


def main():
    logger = dx.info_logger()
    strategy = WindsockTradingStrategy()

    manager = StrategyManager(strategy,
                              server_port=int(os.environ["HTTP_PORT"]),
                              websocket_port=int(os.environ["WEBSOCKET_PORT"]),
                              logger=logger)

    manager.start()
    try:
        while manager.is_alive():
            pass
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop()
        logger.info("Windsock Strategy has been shutdown.")


if __name__ == "__main__":
    main()
