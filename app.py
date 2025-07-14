import streamlit as st
import yfinance as yf
import pandas as pd

# Page config
st.set_page_config(page_title="Penny Stock Tracker", layout="wide")
st.title("📈 Penny Stock Tracker (Live via Yahoo Finance)")
st.caption("Live prices, % change, and volume for penny stocks under $5. Optimized for mobile.")

# Input section
tickers = st.text_input(
    "Enter penny stock tickers (comma-separated):",
    value="RELI, CGTX, MSTY, PTLE, BLDE, AVTX, BNGO"
).upper().replace(" ", "").split(",")

buying_power = st.number_input("Your buying power ($):", min_value=0.0, value=20.0)

@st.cache_data(ttl=60)
def get_stock_data(tickers):
    data = yf.download(tickers, period="1d", interval="1m", group_by='ticker', threads=True)
    results = []

    for ticker in tickers:
        try:
            df = data[ticker]
            current_price = df['Close'].dropna().iloc[-1]
            open_price = df['Open'].dropna().iloc[0]
            percent_change = ((current_price - open_price) / open_price) * 100
            volume = df['Volume'].dropna().iloc[-1]
            shares = int(buying_power // current_price)

            results.append({
                "Ticker": ticker,
                "Price": round(current_price, 3),
                "% Change": round(percent_change, 2),
                "Volume": int(volume),
                "Shares to Buy": shares
            })
        except Exception:
            results.append({
                "Ticker": ticker,
                "Price": "Error",
                "% Change": "Error",
                "Volume": "Error",
                "Shares to Buy": "N/A"
            })

    return pd.DataFrame(results)

# Display
if tickers:
    df_result = get_stock_data(tickers)
    df_result = df_result.sort_values(by="% Change", ascending=False)
    st.dataframe(df_result, use_container_width=True)
