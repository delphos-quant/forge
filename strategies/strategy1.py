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
        while manager.server.is_alive():
            with manager.server.exceptions as exceptions:
                if exceptions:
                    logger.exception(exceptions)
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop()


if __name__ == "__main__":
    main()
