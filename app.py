import streamlit as st
import pandas as pd
from yahoo_fin import stock_info as si

st.set_page_config(page_title="Momentum Alpha Scanner", layout="wide")
st.title("📈 Top 100 NYSE Penny Stock Gainers Under $5")
st.caption("AI-powered penny stock + crypto day trading assistant")

market = st.selectbox("Choose Market", ["NYSE Penny Stocks"])
buying_power = st.number_input("Your Buying Power ($)", min_value=0.0, value=50.0)
refresh_rate = st.selectbox("Refresh Rate", ["Manual", "Every 1 min", "Every 5 min"])

@st.cache_data
def get_nyse_under_5():
    try:
        df = si.get_day_gainers()
        df = df[df['Price (Intraday)'] <= 5.00]
        df = df.head(100)
        df['Shares to Buy'] = (buying_power / df['Price (Intraday)']).astype(int)
        df.rename(columns={
            'Symbol': 'Ticker',
            'Name': 'Name',
            'Price (Intraday)': 'Price',
            '% Change': '% Change',
            'Volume': 'Volume'
        }, inplace=True)
        return df[['Ticker', 'Name', 'Price', '% Change', 'Volume', 'Shares to Buy']]
    except Exception as e:
        st.error(f"Error loading NYSE gainers: {e}")
        return pd.DataFrame()

# Display data
if market == "NYSE Penny Stocks":
    data = get_nyse_under_5()
    if data.empty:
        st.warning("No penny stock gainers found under $5.")
    else:
        st.dataframe(data, use_container_width=True)
