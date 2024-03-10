import os

from dxlib import info_logger
from dxlib.managers import FeedManager
from alpaca.data.live import StockDataStream

from dotenv import load_dotenv
load_dotenv()


def main():
    logger = info_logger("alpaca-markets-feed")
    feed = FeedManager(None, port=os.environ.get("WEBSOCKET_PORT", None), logger=logger)
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
        wss_client.close()
    finally:
        feed.stop()
        logger.info("Feed manager has been shutdown.")


if __name__ == "__main__":
    main()
