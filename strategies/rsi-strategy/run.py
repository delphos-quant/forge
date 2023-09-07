import os

import dxlib as dx
from dxlib import StrategyManager
from dxlib.strategies import RsiStrategy


def main():
    logger = dx.info_logger()
    server_port = int(os.environ["HTTP_PORT"])
    websocket_port = int(os.environ["WEBSOCKET_PORT"])

    strategy = RsiStrategy(upper_bound=80, lower_bound=20)

    manager = StrategyManager(strategy,
                              server_port=server_port,
                              websocket_port=websocket_port,
                              logger=logger)
    manager.start()

    try:
        while manager.is_alive():
            with manager.server.exceptions as exceptions:
                if exceptions:
                    logger.exception(exceptions)
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop()
        logger.info("Strategy manager has been shutdown.")


if __name__ == "__main__":
    main()
