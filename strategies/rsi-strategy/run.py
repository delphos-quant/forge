import os

import dxlib as dx
from dxlib import StrategyManager
from dxlib.strategies import RsiStrategy


def main():
    logger = dx.info_logger()
    server_port = int(os.environ["SERVER_PORT"]) if "SERVER_PORT" in os.environ else 5000
    websocket_port = int(os.environ["WEBSOCKET_PORT"]) if "WEBSOCKET_PORT" in os.environ else 6000

    manager = StrategyManager(RsiStrategy(), server_port=server_port, websocket_port=websocket_port, logger=logger)

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
