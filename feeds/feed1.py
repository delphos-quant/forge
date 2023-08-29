import time
import websocket

from datetime import datetime

from dxlib.api import YFinanceAPI


def on_message(ws, message):
    print("Received Message:", message)


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")


def on_open(ws):
    pass


def date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def main():
    start = date("2022-01-01")
    end = date("2022-12-31")

    data = YFinanceAPI().get_historical_bars(["AAPL", "MSFT", "GOOGL", "AMZN"], start=start, end=end)

    ws_url = "wss://localhost:6001/feed"
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    for _, row in data.iterrows():
        ws.send(row)
        time.sleep(1)


if __name__ == "__main__":
    main()
