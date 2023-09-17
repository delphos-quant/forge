import os
import time

from datetime import datetime

from dxlib.api import YFinanceAPI
from dxlib import info_logger
from dxlib.managers import FeedManager


def date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def main():
    logger = info_logger("feed1")
    start = date("2015-01-01")
    end = date("2022-12-31")

    data = YFinanceAPI().get_historical_bars(["AAPL", "MSFT", "GOOGL", "AMZN"], start=start, end=end)

    def add_delay(rows):
        time.sleep(10)
        for row in rows:
            yield row
            time.sleep(0.1)

    feed = FeedManager(add_delay(data.iterrows()), port=os.environ["WEBSOCKET_PORT"], logger=logger)

    try:
        feed.start()
        while feed.is_alive():
            pass
    except (TypeError, ConnectionError) as e:
        logger.exception(e)
    except KeyboardInterrupt:
        logger.info("User interrupted program")
    finally:
        feed.stop()
        logger.info("Feed manager has been shutdown.")


if __name__ == "__main__":
    main()
