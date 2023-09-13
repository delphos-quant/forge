import pandas as pd

from dxlib import Strategy, History


class WindsockAllocationStrategy(Strategy):
    def __init__(self, predictor=None):
        super().__init__()
        self.predictor = predictor

    def fit(self, history: History):
        pass

    def predict(self, history: History):
        pass

    def execute(
        self, idx, position: pd.Series, history: History
    ) -> pd.Series:
        pass


class WindsockTradingStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.allocation_strategy = WindsockAllocationStrategy()

    def execute(
        self, idx, position: pd.Series, history: History
    ) -> pd.Series:
        pass
