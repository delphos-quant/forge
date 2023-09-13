import os

from dxlib import info_logger
from dxlib.managers import FeedManager
from alpaca.data.live import StockDataStream


def main():
    logger = info_logger("alpaca-markets-feed")
    feed = FeedManager(None, logger=logger)
    feed.start()

    async def feed_handler(data):
        logger.info(data)
        # await feed.handle(data)

    wss_client = StockDataStream(os.environ["APCA-API-KEY-ID"], os.environ["APCA-API-SECRET-KEY"])
    wss_client.subscribe_bars(feed_handler, "AAPL")

    logger.info("Feed manager is running. Press Ctrl+C to stop...")

    try:
        wss_client.run()
    except KeyboardInterrupt:
        pass
    finally:
        feed.stop()
        wss_client.close()
        logger.info("Feed manager has been shutdown.")


if __name__ == "__main__":
    main()
