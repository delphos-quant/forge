import time

import dxlib as dx
from dxlib import StrategyManager
from dxlib.strategies import RsiStrategy


def main():
    logger = dx.info_logger()
    manager = StrategyManager(RsiStrategy(),
                              use_server=True, server_port=5001,
                              use_websocket=True, websocket_port=6001,
                              logger=logger)

    manager.start()

    try:
        while not manager.websocket.is_alive():
            time.sleep(1)

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
