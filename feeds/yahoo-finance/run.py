import time

from datetime import datetime

from dxlib.api import YFinanceAPI
from dxlib import info_logger
from dxlib.managers import FeedManager


def date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def main():
    logger = info_logger("feed1")
    start = date("2022-01-01")
    end = date("2022-12-31")

    data = YFinanceAPI().get_historical_bars(["AAPL", "MSFT", "GOOGL", "AMZN"], start=start, end=end)

    feed = FeedManager(data.iterrows(), "localhost", "6000")
    feed.start()
    delay = 2  # 2 seconds

    try:
        while feed.is_alive():
            if feed.is_socket_alive():
                message = feed.send_snapshot()
                if message is None:
                    logger.info("Feed manager is empty.")
                    break

                logger.info(message)
                time.sleep(delay)
    except (TypeError, ConnectionError) as e:
        logger.exception(e)
    except KeyboardInterrupt:
        logger.info("User interrupted program")
    finally:
        feed.stop()
        logger.info("Feed manager has been shutdown.")


if __name__ == "__main__":
    main()
