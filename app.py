import streamlit as st
import pandas as pd
import numpy as np
import requests

# ========== CONFIG ==========
st.set_page_config(page_title="Momentum Alpha v2.6", layout="wide")
st.title("📈 Momentum Alpha Scanner v2.6")
st.caption("AI-powered penny stock + crypto day trading assistant")

# ========== USER INPUT ==========
market_type = st.selectbox("Choose Market", ["NYSE Penny Stocks", "Top Cryptos"])
buying_power = st.number_input("Your Buying Power ($)", value=20.0, min_value=1.0)
refresh_rate = st.selectbox("Refresh Rate", ["Manual", "Every 1 min", "Every 5 min"])

# ========== DATA FUNCTIONS ==========

def get_nyse_gainers(limit=100):
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=sh_price_u5"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    tables = pd.read_html(response.text)

    for table in tables:
        if "Ticker" in table.columns:
            df = table.copy()
            break
    else:
        st.error("No valid data found.")
        return pd.DataFrame()

    # Clean and rename
    df = df.rename(columns={
        "Ticker": "Ticker",
        "Company": "Name",
        "Price": "Price",
        "Change": "% Change",
        "Volume": "Volume"
    })

    df = df[["Ticker", "Name", "Price", "% Change", "Volume"]]

    # Drop rows with missing values
    df = df.dropna(subset=["Price", "% Change", "Volume"])

    # Convert data types
    df["% Change"] = df["% Change"].astype(str).str.replace('%', '', regex=False).astype(float)
    df["Price"] = df["Price"].astype(str).str.replace('$', '', regex=False).astype(float)
    df["Volume"] = df["Volume"].astype(str).str.replace(',', '', regex=False).astype(int)

    df = df.sort_values(by="% Change", ascending=False).head(limit)

    # Calculate suggested shares to buy
    df["Shares to Buy"] = np.floor(buying_power / df["Price"]).astype(int)

    return df

def get_top_cryptos(limit=50):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "percent_change_24h_desc",
        "per_page": limit,
        "page": 1,
        "price_change_percentage": "24h"
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data)
    df = df[["symbol", "name", "current_price", "price_change_percentage_24h", "total_volume"]]
    df.columns = ["Ticker", "Name", "Price", "% Change", "Volume"]
    df["% Change"] = df["% Change"].round(2)
    df["Shares to Buy"] = np.floor(buying_power / df["Price"]).astype(int)
    return df

# ========== DISPLAY LOGIC ==========

st.markdown("### 📊 Scanning...")

if market_type == "NYSE Penny Stocks":
    st.subheader("📈 Top 100 NYSE Penny Stock Gainers Under $5")
    data = get_nyse_gainers()
else:
    st.subheader("🪙 Top Crypto Gainers")
    data = get_top_cryptos()

if not data.empty:
    st.dataframe(data, use_container_width=True)
else:
    st.warning("⚠️ No data to display. Please try refreshing manually.")
