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

        for security in history.securities:
            # Sample allocation strategy: buy up to 10 shares, sell up to 5 shares
            # If the security is not in the portfolio, then we can buy up to 10 shares
            if position[security].quantity == 0:
                allocation_series[security] = (0, 10)
            # If the security is in the portfolio, then we can sell up to 5 shares
            else:
                allocation_series[security] = (5, 0)

        return allocation_series


class WindsockTradingStrategy(Strategy):
    def __init__(self, volatility_window, liquidity_threshold, price_threshold, stop_loss_pct, profit_target_pct):
        super().__init__()
        self.volatility_window = volatility_window
        self.liquidity_threshold = liquidity_threshold
        self.price_threshold = price_threshold
        self.stop_loss_pct = stop_loss_pct
        self.profit_target_pct = profit_target_pct
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
        # Calculate ATR (Average True Range) as a measure of volatility
        atr = self.calculate_atr(recent_prices[security])

        # Check if the stock price is below the price threshold
        price = recent_prices[security].iloc[-1]
        price_below_threshold = price < self.price_threshold

        # Check if trading volume exceeds the liquidity threshold
        volume = recent_prices['Volume'][security].iloc[-1]
        volume_above_threshold = volume > self.liquidity_threshold

        # Implement more advanced criteria, such as mean reversion and momentum
        mean_return = self.calculate_mean_return(recent_prices[security])
        momentum = self.calculate_momentum(recent_prices[security])

        return (
                atr > 0 and
                price_below_threshold and
                volume_above_threshold and
                mean_return < 0 < momentum
        )

    @classmethod
    def calculate_atr(cls, prices, window=14):
        # Calculate True Range (TR)
        high = prices['High']
        low = prices['Low']
        close = prices['Close']
        tr = np.maximum(high - low, np.abs(high - close.shift(1)), np.abs(low - close.shift(1)))

        # Calculate ATR using a simple moving average (SMA)
        atr = tr.rolling(window=window).mean()

        return atr

    @classmethod
    def calculate_mean_return(cls, prices, lookback_window=5):
        # Calculate mean return over a lookback period
        returns = prices.pct_change().dropna()
        mean_return = returns.rolling(window=lookback_window).mean().iloc[-1]
        return mean_return

    @classmethod
    def calculate_momentum(cls, prices, lookback_window=10):
        # Calculate momentum as the rate of change over a lookback period
        returns = prices.pct_change().dropna()
        momentum = (1 + returns).rolling(window=lookback_window).apply(np.prod, raw=True) - 1
        return momentum

    def generate_trade_signal(self, price):
        # Generate trade signal based on breakout
        if price > self.price_threshold:
            return Signal(TradeType.BUY, 1, price)
        else:
            return Signal(TradeType.WAIT)
