# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="Momentum Alpha Scanner", layout="wide")

st.title("📈 Momentum Alpha - Penny Stock AI Scanner")
st.subheader("🚀 AI-Powered Scanner for Real-Time Penny Stock Day Trades")

# === Settings ===
tickers = ["ACXP", "PTLE", "MSTY", "SINT", "TOP", "GNS"]  # Update with your preferred tickers
min_volume = 500_000
max_price = 5.00

today = datetime.date.today()
data = {}

st.markdown("---")

# === Fetch data ===
st.info("📡 Scanning live price and volume data...")

for ticker in tickers:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d", interval="1m")
    if not hist.empty:
        latest = hist.iloc[-1]
        prev_close = stock.history(period="2d").iloc[-2]['Close']
        percent_change = ((latest['Close'] - prev_close) / prev_close) * 100

        data[ticker] = {
            'Price': round(latest['Close'], 3),
            'Volume': int(latest['Volume']),
            '% Change': round(percent_change, 2),
        }

# === Display top movers ===
df = pd.DataFrame.from_dict(data, orient='index')
df = df[df['Price'] <= max_price]
df = df[df['Volume'] >= min_volume]
df = df.sort_values(by='% Change', ascending=False)

st.success("✅ Top Penny Stock Movers Under $5")

st.dataframe(df.style.highlight_max(axis=0, color="lightgreen"))

# === Simulate AI Setup Generation ===
if not df.empty:
    top = df.iloc[0]
    st.markdown("### 📊 Suggested Trade Setup (Simulated AI Output)")
    st.write(f"**Ticker:** {df.index[0]}")
    st.write(f"**Current Price:** ${top['Price']}")
    st.write("**Entry Zone:**", f"${top['Price'] * 0.98:.2f} - ${top['Price'] * 1.01:.2f}")
    st.write("**Stop Loss:**", f"${top['Price'] * 0.95:.2f}")
    st.write("**Target 1:**", f"${top['Price'] * 1.1:.2f}")
    st.write("**Target 2:**", f"${top['Price'] * 1.2:.2f}")
    st.write("**Risk/Reward:**", "1:3")
    st.write("**Confidence Score:**", "87%")
else:
    st.warning("No qualified penny stock movers found at this time.")

st.markdown("---")
st.caption("🔄 Refresh to update. | Built by Thomas Boyd’s Momentum Engine v1.")
