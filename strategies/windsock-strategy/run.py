from collections import defaultdict
from datetime import datetime

import pandas as pd
import numpy as np
import plotly.express as px

import dxlib as dx
from dxlib import StrategyManager, TradeType

from strategy import WindsockTradingStrategy


def annualized_return_dates(final, start, start_date, end_date):
    # Convert the date strings to datetime objects
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    # Calculate the number of days between the two dates
    number_of_days = (end_datetime - start_datetime).days

    # Convert the number of days to years (assuming 365 days per year)
    number_of_years = number_of_days / 365.0

    return ((final / start) ** (1 / number_of_years) - 1) * 100


def main():
    logger = dx.no_logger()

    symbols = pd.read_csv("Symbols.csv")
    print(symbols)

    np.random.seed(101)

    historical_bars = dx.api.YFinanceAPI().get_historical_bars(symbols.sample(100).values.flatten(),
                                                               start="2021-01-01", end="2023-06-06")

    history = dx.History(historical_bars)

    manager = StrategyManager(WindsockTradingStrategy(), logger=logger)
    portfolio = dx.Portfolio(name="windsock")

    starting_cash = 1_000_000
    portfolio.add_cash(starting_cash)
    manager.register_portfolio(portfolio)

    try:
        manager.run(history)
    except KeyboardInterrupt:
        pass
    finally:
        logger = dx.info_logger("Metrics")
        logger.info("Windsock Strategy finished.")

        position = portfolio.position

        # Calculate position using position (dict) and last history close prices (pd.Series)
        # if security is in position, sum to value:
        value = 0
        for security, quantity in position.items():
            value += quantity * (history.df["Close", security].dropna().iloc[-1] * 0.98 - 2)
        total_value = value + portfolio.current_cash

        total_profit = total_value - starting_cash
        annualized_return = annualized_return_dates(total_value, starting_cash, "2021-01-01", "2023-06-06")

        historical_quantity = portfolio.historical_quantity(history)
        px.line(historical_quantity, title="Inventário histórico do portfólio").show()

        history_c = history.df["Close"].copy()
        temp = (history_c * historical_quantity.drop(portfolio.security_manager.cash, axis=1)).sum(axis=1)
        drawdown = (temp / temp.cummax() - 1).fillna(0) * 100
        max_drawdown = drawdown.max()

        history_c[portfolio.security_manager.cash] = 1
        historical_value = history_c * historical_quantity

        portfolio_historical_value = historical_value.sum(axis=1)

        px.line(portfolio_historical_value, title="Valor histórico do portfolio").show()

        px.line(drawdown, title="Drawdown histórico do Portfolio", labels={"value": "Drawdown"}).show()

        # Calculating winning and losing trades
        security_transactions = defaultdict(list)

        for transaction in portfolio.transaction_history:
            security = transaction.security
            security_transactions[security].append(transaction)

        # Initialize dictionaries to store winning and losing trades for each symbol
        winning_trades = defaultdict(list)
        losing_trades = defaultdict(list)

        avg_trades_per_month = 0
        trades_per_month = defaultdict(list)

        for security, transactions in security_transactions.items():
            buying_price = 0
            pnl = 0
            for transaction in transactions:
                if transaction.timestamp != -1 and transaction.security != portfolio.security_manager.cash:
                    year = transaction.timestamp.year
                    month = transaction.timestamp.month
                    trades_per_month[(year, month)].append(transaction)

                if transaction.security == portfolio.security_manager.cash:
                    continue
                if transaction.trade_type == TradeType.BUY:
                    buying_price = transaction.price if transaction.price else 1
                    pnl = -buying_price * transaction.quantity  # Negative because you spent money to buy
                elif transaction.trade_type == TradeType.SELL:
                    selling_price = transaction.price
                    pnl = selling_price * transaction.quantity - buying_price * transaction.quantity

                if pnl > 0:
                    winning_trades[security].append(pnl)
                elif pnl < 0:
                    losing_trades[security].append(pnl)

        avg_trades_per_month = sum(len(trades) for trades in trades_per_month.values()) / len(trades_per_month)

        logger.info(f"Average trades per month: {avg_trades_per_month}")

        # # Calculate the total profit and total loss for each symbol
        # total_profit = {symbol: sum(profits) for symbol, profits in winning_trades.items()}
        # total_loss = {symbol: sum(losses) for symbol, losses in losing_trades.items()}
        # # Sum current position to total_profit:
        # for security, quantity in position.items():
        #     if security != portfolio.security_manager.cash and quantity > 0:
        #         if security in total_profit:
        #             total_profit[security] += quantity * (history.df["Close", security].dropna().iloc[-1] * 0.98 - 2)
        #         else:
        #             total_profit[security] = quantity * (history.df["Close", security].dropna().iloc[-1] * 0.98 - 2)
        #
        # # Calculate the number of winning and losing trades for each symbol
        # num_winning_trades = {symbol: len(profits) for symbol, profits in winning_trades.items()}
        # num_losing_trades = {symbol: len(losses) for symbol, losses in losing_trades.items()}
        #
        # avg_num_winning_trades = sum(num_winning_trades.values()) / len(num_winning_trades)
        # avg_num_losing_trades = sum(num_losing_trades.values()) / len(num_losing_trades)

        logger.info(f"Portfolio value: {value}")
        logger.info(f"Portfolio cash: {portfolio.current_cash}")

        # Maps symbol to list of trades (a trade is a period when started with 0 assets, ended with 0 assets),
        # each entry in the list is an amount profited or lost in a trade
        # Use portfolio.historical_quantity as well as history.df["Close", security] to calculate profit/loss

        logger.info(f"Returns: {starting_cash} -> {total_value} = {annualized_return}%")

        with open("transactions.csv", "w+") as f:
            f.write("Security,Trade Type,Quantity,Price,Date\n")
            for transaction in portfolio.transaction_history:
                f.write(f"{transaction.security},{transaction.trade_type},"
                        f"{transaction.quantity},{transaction.price},{transaction.timestamp}\n")


if __name__ == "__main__":
    main()
