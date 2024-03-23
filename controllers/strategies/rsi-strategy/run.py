import asyncio
import os
from typing import AsyncGenerator

import dxlib as dx
from dxlib.interfaces.internal import MarketInterface
from dxlib.strategies.custom_strategies import RsiStrategy


def main():
    interface_port = int(os.environ.get("INTERFACE_PORT", 4001))
    http_port = int(os.environ.get("HTTP_PORT"))

    strategy = RsiStrategy(field="price")
    market_interface = MarketInterface(host=f"0.0.0.0")

    logger = dx.InfoLogger()
    executor = dx.Executor(strategy)
    executor_interface = dx.ExecutorInterface(executor)
    http_server = dx.HTTPServer(host="0.0.0.0", port=http_port, logger=logger)
    http_server.add_interface(executor_interface)
    try:
        http_server.start()
        quotes = market_interface.listen(market_interface.quote_stream, port=interface_port, retry=1)

        def get_first_element_sync(async_gen):
            async def fetch_first_element():
                async for item in async_gen:
                    return item

            loop = asyncio.get_event_loop()
            return loop, loop.run_until_complete(fetch_first_element())

        loop, history = get_first_element_sync(quotes)
        schema = history.schema

        async def bar_generator(history_quotes: AsyncGenerator):
            try:
                async for history_quote in history_quotes:
                    history_quote.schema = schema
                    for bar in history_quote:
                        yield bar
            except KeyboardInterrupt:
                raise

        signals: AsyncGenerator = executor.run(bar_generator(quotes), input_schema=schema)

        async def print_signals():
            async for signal in signals:
                print(signal)

        loop.run_until_complete(print_signals())

    except KeyboardInterrupt:
        pass
    finally:
        http_server.stop()
        logger.info("Stopping strategy...")


if __name__ == "__main__":
    main()
