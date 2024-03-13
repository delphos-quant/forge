import asyncio
import os
import time
from typing import AsyncGenerator

import dxlib as dx
from dxlib.interfaces.internal import MarketInterface
from dxlib.strategies.custom_strategies import RsiStrategy


def main():
    logger = dx.InfoLogger()
    interface_port = int(os.environ.get("INTERFACE_PORT", 4001))

    strategy = RsiStrategy(field="price")
    interface = MarketInterface(host="localhost")

    executor = dx.Executor(strategy)
    ws = None
    try:
        ws, quotes = interface.listen(interface.quote_stream, port=interface_port)

        async def await_history():
            return await quotes.__anext__()

        history = asyncio.run(await_history())
        schema = history.schema

        async def bar_generator():
            async for history in quotes:
                history.schema = schema
                for bar in history:
                    yield bar

        signals: AsyncGenerator = executor.run(bar_generator(), input_schema=schema)

        # create thread to print signals
        async def print_signals():
            async for signal in signals:
                print(signal)
                # send ping

        # thread
        t = asyncio.run(print_signals())

        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        if ws:
            ws.close()
        logger.info("Strategy manager has been shutdown.")


if __name__ == "__main__":
    main()
