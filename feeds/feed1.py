import time
import threading
from typing import AsyncGenerator

import websocket
import json
import asyncio
from datetime import datetime

from dxlib import info_logger, History, Security
from dxlib.api import YFinanceAPI


class FeedManager:
    MAX_RETRIES = 5
    RETRY_INTERVAL_SECONDS = 1

    def __init__(self, subscription, ip="localhost", port="6001", secure=False, retry=False, logger=None):
        self._ws_url = f"ws{'s' if secure else ''}://{ip}:{port}"
        self.subscription = subscription
        self.retry = retry

        self._ws = None
        self.thread = None
        self._running = threading.Event()
        self.logger = info_logger() if logger is None else logger
        self.current_retries = 0

    def _connect(self):
        self._ws = websocket.WebSocketApp(self._ws_url,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)

    def _serve(self):
        if self._running.is_set():
            self.current_retries = 0

            while self.current_retries < (self.MAX_RETRIES if self.retry else 1):
                time.sleep(self.RETRY_INTERVAL_SECONDS * self.current_retries)
                try:
                    self._connect()
                    self._ws.run_forever()

                    if not self.is_socket_alive():
                        raise ConnectionError("Socket could not connect")
                    return

                except KeyboardInterrupt:
                    return
                except Exception as e:
                    self.logger.warning(f"Connection attempt {self.current_retries + 1}/{self.MAX_RETRIES} failed: {e}")
                    self.current_retries += 1

            if self.current_retries >= self.MAX_RETRIES:
                self._running.clear()
                self.logger.exception("Max retries reached, giving up on connection")

    def start(self):
        self.logger.info(f"Connecting to websocket on {self._ws_url}")
        if self.thread is None:
            self._running.set()
            self.thread = threading.Thread(target=self._serve)
            self.thread.start()

    def stop(self):
        if self._ws:
            self._ws.close()
        self._ws = None
        self._running.clear()

        self.thread.join()
        self.thread = None

    def restart(self):
        self.stop()
        self.start()

    def send_message(self, message):
        self._ws.send(message)

    def send_snapshot(self):
        try:
            data = History(next(self.subscription)).to_dict()
        except StopIteration:
            self.logger.warning("Subscription has ended")
            return None
        message = {"snapshot": data}
        self.send_message(json.dumps(message))
        return message

    def on_message(self, ws, message):
        print("Received Message:", message)

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.warning(f"Websocket closed with status code {close_status_code}: {close_msg}")

    def on_open(self, ws):
        self.current_retries = 0
        self.logger.info("Connected to websocket. Press Ctrl+C to stop...")
        pass

    def is_alive(self):
        return self._running.is_set()

    def is_socket_alive(self):
        return self._ws and self._ws.sock and self._ws.sock.connected


def date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def main():
    logger = info_logger("feed1")
    start = date("2022-01-01")
    end = date("2022-12-31")

    data = YFinanceAPI().get_historical_bars(["AAPL", "MSFT", "GOOGL", "AMZN"], start=start, end=end)

    feed = FeedManager(data.iterrows())
    feed.start()
    delay = 1

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
