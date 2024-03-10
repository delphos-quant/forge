import os
import time

import dxlib as dx


def main():
    interface_port = int(os.environ.get("INTERFACE_PORT", 8001))
    logger = dx.InfoLogger()
    interface = dx.MarketInterface(dx.YFinanceAPI())
    server = dx.HTTPServer(port=interface_port, logger=logger)

    server.add_interface(interface)

    try:
        server.start()

        while server.alive:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


if __name__ == "__main__":
    main()
    print("yahoo-finance/run.py executed successfully.")
