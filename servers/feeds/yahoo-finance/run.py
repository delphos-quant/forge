import os
import time

import dxlib as dx


def main():
    http_port = int(os.environ.get("HTTP_PORT"))
    websocket_port = int(os.environ.get("WEBSOCKET_PORT"))

    logger = dx.InfoLogger()
    interface = dx.MarketInterface(dx.YFinanceAPI())
    http_server = dx.HTTPServer(host="0.0.0.0", port=http_port, logger=logger)
    websocket_server = dx.WebsocketServer(host="0.0.0.0", port=websocket_port, logger=logger)

    http_server.add_interface(interface)
    websocket_server.add_interface(interface)

    try:
        http_server.start()
        websocket_server.start()

        while not (http_server.alive and websocket_server.alive):
            time.sleep(1)

        websocket_server.listen(interface.quote_stream, tickers=["BTC-USD", "NVDC34.SA"], interval=1)

        while http_server.alive and websocket_server.alive:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        http_server.stop()
        websocket_server.stop()


if __name__ == "__main__":
    main()
    print("yahoo-finance/run.py executed successfully.")
