import time
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


@st.experimental_memo
def get_stock_data(symbol="BTC-USD"):
    api = dx.interfaces.YFinanceAPI()
    return api.quote([symbol], interval="1m")


# Initial stock symbol
stock_symbol = "BTC-USD"

# Dashboard title
st.title("Real-Time / Live Data Science Dashboard")

# Single-element container
placeholder = st.empty()

price_history = pd.DataFrame()
security_manager = dx.SecurityManager.from_list([stock_symbol])

quote_history = dx.History(schema=dx.Schema(
    levels=[dx.SchemaLevel.DATE, dx.SchemaLevel.SECURITY],
    fields=["price"],
    security_manager=security_manager)
)

signal_history = dx.History(schema=dx.Schema(
    levels=[dx.SchemaLevel.DATE, dx.SchemaLevel.SECURITY],
    fields=["signal"],
    security_manager=security_manager)
)

for seconds in range(200):
    # Fetch real-time stock data
    quote = get_stock_data(stock_symbol)

    price = quote.df.droplevel('security')['price']
    current_time = pd.Timestamp.now()
    price.index = [current_time] * len(price)
    price_history = pd.concat([price_history, pd.DataFrame(price)])
    average_price = price.mean()

    quote_history.add(quote)
    signals = strategy.execute(((current_time, stock_symbol), quote), quote_history)
    signal_history.add(signals)
    quantity = (signals.iloc[0].quantity or 0) * signals.iloc[0].side.value

    with placeholder.container():
        # Create three columns
        kpi1, kpi2, kpi3 = st.columns(3)

        # Fill in those three columns with respective metrics or KPIs
        kpi1.metric(
            label="Average Price 💹",
            value=f"${round(average_price, 2)}",
            delta=round(average_price) - 10,
        )

        kpi3.metric(
            label="Stock Symbol 📈",
            value=f"{stock_symbol}",
            delta=0,
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

        st.markdown("### Detailed Data View")
        st.dataframe(price_history)
        time.sleep(5)

if __name__ == "__main__":
    pass
