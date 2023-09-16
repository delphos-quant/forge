import numpy as np
import pandas as pd

from dxlib import Strategy, History, Signal, TradeType


class WindsockAllocationStrategy(Strategy):
    def __init__(self, predictor=None):
        super().__init__()
        self.predictor = predictor

    def fit(self, history: History):
        pass

    def predict(self, history: History):
        pass

    def execute(self, idx, position: pd.Series, history: History) -> pd.Series:
        # Define the lower and upper bounds for buy and sell quantities
        # For example, [(5, 10)] means no more than 5 can be sold, and no more than 10 can be bought of the security.
        allocation_series = pd.Series([np.inf, np.inf], index=history.securities.values())

        for security in history.securities.values():
            # Sample allocation strategy: buy up to 10 shares, sell up to 5 shares
            if position[security] == 0:
                allocation_series[security] = (0, 1)
            else:
                allocation_series[security] = (1, 1)

        return allocation_series


class WindsockTradingStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.allocation_strategy = WindsockAllocationStrategy()

    def execute(self, idx, position: pd.Series, history: History) -> pd.Series:
        signals = pd.Series(Signal(TradeType.WAIT), index=history.securities.values())
        loc = history.df.index.get_loc(idx)

        if loc >= self.volatility_window:
            recent_prices = history.df.iloc[loc - self.volatility_window + 1:loc + 1]

            for security in recent_prices.columns:
                if self.meets_strategy_criteria(security, recent_prices):
                    price = recent_prices[security].iloc[-1]
                    signal = self.generate_trade_signal(price)

                    allocation_bounds = self.allocation_strategy.execute(idx, position, history)
                    min_sell_qty, max_buy_qty = allocation_bounds[security]

                    if signal.trade_type == TradeType.BUY:
                        signal.quantity = min(max_buy_qty, position[security] // price)
                    elif signal.trade_type == TradeType.SELL:
                        signal.quantity = min(min_sell_qty, position[security])

                    signals[security] = signal

        return signals

    def meets_strategy_criteria(self, security, recent_prices):
        atr = self.calculate_atr(recent_prices[security])

        price = recent_prices[security].iloc[-1]
        price_below_threshold = price < self.price_threshold

        volume = recent_prices['Volume'][security].iloc[-1]
        volume_above_threshold = volume > self.liquidity_threshold

        mean_return = self.calculate_mean_return(recent_prices[security])
        momentum = self.calculate_momentum(recent_prices[security])

        return (
                atr > 0 and
                price_below_threshold and
                volume_above_threshold and
                mean_return < 0 < momentum
        )

    @classmethod
    def atr(cls, history, window=14):
        high = history.df['High']
        low = history.df['Low']
        close = history.df['Close']
        tr = np.maximum(high - low, np.abs(high - close.shift(1)), np.abs(low - close.shift(1)))

        atr = tr.rolling(window=window).mean()

        return atr

    @classmethod
    def adtv(cls, history, short_window=5, long_window=60):
        volume = history.df["Volume"]

        adtv_short = volume.rolling(window=short_window).mean()
        adtv_long = volume.rolling(window=long_window).mean()

        adtv = adtv_short / adtv_long
        log_change = np.log(adtv - adtv.shift(1))

        market_log_change = log_change.mean()
        market_log_volatility = log_change.std()

        normalized_log_change = (log_change - market_log_change) / market_log_volatility

        return normalized_log_change

    @classmethod
    def calculate_momentum(cls, prices, lookback_window=10):
        returns = prices.pct_change().dropna()
        momentum = (1 + returns).rolling(window=lookback_window).apply(np.prod, raw=True) - 1
        return momentum

    def generate_trade_signal(self, price):
        if price > self.price_threshold:
            return Signal(TradeType.BUY, 1, price)
        else:
            return Signal(TradeType.WAIT)
