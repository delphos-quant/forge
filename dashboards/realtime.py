import time

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import dxlib as dx

st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="✅",
    layout="wide",
)

strategy = dx.strategies.RsiStrategy(reverse=True, field="price", window=14, upper=70, lower=30)


@st.cache_data
def get_stock_data(symbol="BTC-USD"):
    api = dx.interfaces.YFinanceAPI()
    return api.quote([symbol], interval="1m")


# Initial stock symbol
stock_symbol = "BTC-USD"

# Dashboard title
st.title("Real-Time / Live Data Science Dashboard")

# Single-element container
placeholder = st.empty()

security_manager = dx.SecurityManager.from_list([stock_symbol])
btc = security_manager.get(stock_symbol)

price_history = dx.History(schema=dx.Schema(
    levels=[dx.SchemaLevel.DATE, dx.SchemaLevel.SECURITY],
    fields=["price"],
    security_manager=security_manager)
)

signal_history = dx.History(schema=dx.Schema(
    levels=[dx.SchemaLevel.DATE, dx.SchemaLevel.SECURITY],
    fields=["signal"],
    security_manager=security_manager)
)

portfolio_cash = [starting_cash := 1e4]
assets = [0]
assets_value = [0]

price_df = pd.DataFrame()
quote = get_stock_data(stock_symbol)
price = quote.df.droplevel('security')['price']
current_time = pd.Timestamp.now()
price.index = [current_time] * len(price)
price_df = pd.concat([price_df, pd.DataFrame(price)])

price_history.add(price_df)

def portfolio_value(idx):
    return portfolio_cash[idx] + assets_value[idx]


for seconds in range(200):
    # Simulate new price using previous price from price_history
    prev_price = price_df.iloc[-1]
    new_price = prev_price + np.random.normal(0.5, 2)
    new_price = pd.DataFrame(new_price).T
    current_time = pd.Timestamp.now()
    new_price.index = [current_time] * len(new_price)
    price_df = pd.concat([price_df, pd.DataFrame(new_price)])
    average_price = new_price.mean()['price']

    price_history.add(new_price)
    signals = strategy.execute(((current_time, btc), quote), price_history)
    orders = dx.OrderInterface.execute_signals(signals)
    # get order_value
    order_size = (orders[0].data.quantity or 0) * orders[0].data.side.value
    order_value = order_size * price[-1]
    # update portfolio_cash
    portfolio_cash.append(portfolio_cash[-1] - order_value)
    # update assets
    assets.append(assets[-1] + order_value)
    assets_value.append(assets[-1] * price[-1])
    print(signals)

    with placeholder.container():
        # Create three columns
        kpi1, kpi2, kpi3 = st.columns(3)

        # Fill in those three columns with respective metrics or KPIs
        kpi1.metric(
            label="Average Price 💹",
            value=f"${round(average_price, 2)}",
            delta=round(average_price) - 10,
        )

        # how many time steps passed
        kpi2.metric(
            label="Time Step ⏱️",
            value=f"{seconds}",
            delta=1,
        )

        kpi3.metric(
            label="Stock Symbol 📈",
            value=f"{stock_symbol}",
        )

        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### Price Chart")
            fig = px.line(
                data_frame=price_history,
                y="price",
                labels={"price": "Stock Price"},
            )
            st.plotly_chart(fig)

        # use def portfolio_value to get the portfolio value
        df = pd.DataFrame({
            "Portfolio Value": [portfolio_value(i) for i in range(len(portfolio_cash))],
            "Time": pd.date_range(start=pd.Timestamp.now(), periods=len(portfolio_cash), freq="1min")
        })
        with fig_col2:
            st.markdown("### Portfolio Value")
            fig = px.line(
                data_frame=df,
                x="Time",
                y="Portfolio Value",
                labels={"price": "Stock Price"},
            )
            st.plotly_chart(fig)

        st.markdown("### Detailed Data View")
        st.dataframe(price_history)
        time.sleep(1)

if __name__ == "__main__":
    pass
