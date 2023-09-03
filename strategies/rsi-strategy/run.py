import os

import dxlib as dx
from dxlib import StrategyManager
from dxlib.strategies import RsiStrategy


def main():
    logger = dx.info_logger()
    manager = StrategyManager(RsiStrategy(),
                              use_server=True,
                              server_port=int(os.environ["SERVER_PORT"]) if "SERVER_PORT" in os.environ
                              else None,
                              use_websocket=True,
                              websocket_port=int(os.environ["WEBSOCKET_PORT"]) if "WEBSOCKET_PORT" in os.environ
                              else None,
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
