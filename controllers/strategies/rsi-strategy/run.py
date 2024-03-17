import asyncio
import os
from typing import AsyncGenerator

import dxlib as dx
from dxlib.interfaces.internal import MarketInterface
from dxlib.strategies.custom_strategies import RsiStrategy


def main():
    logger = dx.InfoLogger()
    interface_port = int(os.environ.get("INTERFACE_PORT", 4001))

    strategy = RsiStrategy(field="price")
    interface = MarketInterface(host="0.0.0.0")

    executor = dx.Executor(strategy)
    try:
        quotes: AsyncGenerator = interface.listen(interface.quote_stream, port=interface_port, retry=5)

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
        logger.info("Stopping strategy...")


if __name__ == "__main__":
    main()
