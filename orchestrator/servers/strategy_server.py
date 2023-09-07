from .server import Server, Service
from dxlib.strategies import Strategy
import hashlib


class StrategyServer(Server):
    def __init__(self):
        super().__init__()
        self._strategies: dict[str, Service] = {}

    def start_strategy(self, identifier: str):
        if identifier in self._strategies:
            self._strategies[identifier].start()

    def stop_strategy(self, identifier: str):
        if identifier in self._strategies:
            self._strategies[identifier].stop()
