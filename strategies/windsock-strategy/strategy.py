import numpy as np
import pandas as pd

from dxlib import Strategy, History, Signal, TradeType


class WindsockAllocationStrategy:
    def __init__(self, predictor=None):
        super().__init__()
        self.predictor = predictor

    def fit(self, history: History):
        pass

    def predict(self, history: History):
        pass

    def execute(self, idx, position: pd.Series, history: History) -> tuple[pd.Series, pd.Series]:
        # Define the lower and upper bounds for buy and sell quantities
        # For example, [(5, 10)] means no more than 5 can be sold, and no more than 10 can be bought of the security.
        buy = pd.Series(1, index=history.securities.values())
        sell = pd.Series(0, index=history.securities.values())

        for security in position.index:
            if position[security] > 0:
                sell[security] = 1

        return sell, buy


class WindsockTradingStrategy(Strategy):
    def __init__(self, short_window=14, long_window=60, liquidity_threshold=.9, growth_threshold=.05):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        self.liquidity_threshold = liquidity_threshold
        self.growth_threshold = growth_threshold
        self.allocation_strategy = WindsockAllocationStrategy()

    def execute(self, idx, position: pd.Series, history: History) -> pd.Series:
        loc = history.df.index.get_loc(idx)

        if loc >= self.long_window:
            signals = self.get_signals(history)
            quantities = self.allocation_strategy.execute(idx, position, history)

            return self.set_quantity(signals, quantities)
        else:
            return pd.Series(Signal(TradeType.WAIT), index=history.securities.values())

    @classmethod
    def set_quantity(cls, signals: pd.Series, quantities: tuple[pd.Series, pd.Series]):
        sell_quantities, buy_quantities = quantities

        for security in signals.index:
            if signals[security].trade_type == TradeType.BUY:
                signals[security].quantity = buy_quantities[security]
            elif signals[security].trade_type == TradeType.SELL:
                signals[security].quantity = sell_quantities[security]

        return signals

    def get_signals(self, history):
        adtv = self.adtv(history)
        breakout = self.breakout(history)

        momentum = self.momentum(adtv).iloc[-1]

        signals = pd.Series(Signal(TradeType.WAIT), index=history.securities.values())
        prices = history.df["Close"].iloc[-1]

        for security in history.securities.values():
            if breakout[security] and adtv[security].iloc[-1] > self.liquidity_threshold:
                if momentum[security] > self.growth_threshold:
                    signals[security] = Signal(TradeType.BUY, quantity=1, price=prices[security])
                elif momentum[security] < -self.growth_threshold:
                    signals[security] = Signal(TradeType.SELL, quantity=1, price=prices[security])

        return signals

    def atr(self, history):
        high = history.df['High']
        low = history.df['Low']
        close = history.df['Close']
        tr = np.maximum(high - low, np.abs(high - close.shift(1)), np.abs(low - close.shift(1)))

        atr = tr.rolling(window=self.short_window).mean()

        return atr

    def adtv(self, history):
        volume = history.df["Volume"]

        relative_adtv = volume.rolling(window=self.short_window).mean() / volume.rolling(window=self.long_window).mean()
        change = relative_adtv.pct_change()

        mean = change.mean()
        std = change.std().fillna(1)

        return (change - mean) / std

    def momentum(self, value):
        change = value.pct_change()
        momentum = (1 + change).rolling(window=self.short_window).apply(np.prod, raw=True) - 1
        return momentum

    def breakout(self, history) -> pd.Series:
        volatility = history.indicators.volatility()
        upper, lower = history.indicators.bollinger_bands(self.short_window)
        upper = upper["Close"]
        lower = lower["Close"]
        volatility = volatility["Close"]
        var_mean = (upper - lower).mean()
        var_var = (upper - lower).std() + 1e-6

        var_historical = ((upper - lower) - var_mean) / var_var
        var_normalized = (volatility - var_mean) / var_var

        # PyCharm is complaining about the following line, but it works fine. (Added suppress to the warning.)
        # noinspection PyTypeChecker
        return abs(var_normalized.iloc[-1]) > abs(var_historical.iloc[-1])
