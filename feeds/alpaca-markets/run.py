import os

from dxlib import info_logger
from dxlib.managers import FeedManager
from alpaca.data.live import StockDataStream


def main():
    logger = info_logger("alpaca-markets-feed")
    feed = FeedManager(None, os.environ["HOST"], os.environ["PORT"], retry=False, logger=logger)
    try:
        feed.start()
        while not feed.is_socket_alive():
            if feed.timeout:
                raise ConnectionError("Feed manager timed out.")
    except KeyboardInterrupt:
        logger.info("User interrupted program")
        feed.stop()
        return

    async def feed_handler(data):
        feed.send_snapshot(data)

    wss_client = StockDataStream(os.environ["APCA-API-KEY-ID"], os.environ["APCA-API-SECRET-KEY"])
    wss_client.subscribe_bars(feed_handler, "AAPL")

    logger.info("Feed manager is running. Press Ctrl+C to stop...")

    try:
        wss_client.run()
    except KeyboardInterrupt:
        pass
    finally:
        feed.stop()
        logger.info("Feed manager has been shutdown.")
        wss_client.close()


if __name__ == "__main__":
    main()
