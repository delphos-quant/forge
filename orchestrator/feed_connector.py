import dxlib
from dxlib.managers import Connector


def main():
    c = Connector({"alpaca": "ws://localhost:6000"})
    logger = dxlib.info_logger("connector")

    try:
        logger.info("Starting connector...")
        c.start()
    except ConnectionRefusedError:
        logger.error("Connection refused. Is the server running?")
        c.stop()
    finally:
        logger.info("Connector has been shutdown.")


if __name__ == "__main__":
    main()
