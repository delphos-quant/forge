import os

import dxlib as dx
from dxlib.interfaces.internal import StrategyHTTPInterface
from dxlib.strategies.custom_strategies import RsiStrategy


def main():
    logger = dx.DebugLogger()
    server_port = int(os.environ["HTTP_PORT"])

    strategy = RsiStrategy(upper_bound=80, lower_bound=20)

    interface = StrategyHTTPInterface(strategy)

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
