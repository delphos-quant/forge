import time
import threading
import websocket
from websocket import WebSocketException
from datetime import datetime

from dxlib import info_logger, History
from dxlib.api import YFinanceAPI


class FeedManager:
    def __init__(self, subscription, ws_url="ws://localhost:6001"):
        self._ws = websocket.WebSocketApp(ws_url,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)
        self.thread = None
        self.subscription = subscription
        self._running = threading.Event()

    def _serve(self):
        if self._running.is_set():
            try:
                self._ws.run_forever()
            except WebSocketException:
                print("WebSocket closed")
                time.sleep(1)
            except KeyboardInterrupt:
                self._ws.close()

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._serve)
            self._running.set()
            self.thread.start()

    def stop(self):
        self._running.clear()
        self._ws.close()
        self.thread.join()

    def send_message(self, message):
        self._ws.send(message)

    def on_message(self, ws, message):
        print("Received Message:", message)

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")

    def on_open(self, ws):
        pass

    def is_alive(self):
        return self._running.is_set()


def date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def main():
    logger = info_logger("feed1")
    start = date("2022-01-01")
    end = date("2022-12-31")

    data = YFinanceAPI().get_historical_bars(["AAPL", "MSFT", "GOOGL", "AMZN"], start=start, end=end)

    feed = FeedManager(data.iterrows())
    delay = 1

    feed.start()
    try:
        while feed.is_alive():
            snapshot = History(feed.subscription.__next__()).to_json()
            logger.info(snapshot)
            feed.send_message(snapshot)
            time.sleep(delay)
    except (WindowsError, TypeError, websocket.WebSocketException) as e:
        logger.exception(e)
    finally:
        feed.stop()
        logger.info("Feed manager has been shutdown.")


if __name__ == "__main__":
    main()
