import dxlib
from dxlib.managers import Connector


def main():
    c = Connector({"yfinance": {"uri": "ws://localhost:7002", "data_type": "snapshot"}}, http_port=8000)
    logger = dxlib.info_logger("connector")

    try:
        logger.info("Starting connector...")
        c.start()
    except ConnectionRefusedError:
        logger.error("Connection refused. Is the server running?")
        c.stop()
    except KeyboardInterrupt:
        logger.info("User interrupted program.")
        c.stop()
    finally:
        logger.info("Connector has been shutdown.")


if __name__ == "__main__":
    main()
