import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Momentum Alpha v2.5+", layout="wide")
st.title("📈 Top 100 NYSE Penny Stock Gainers Under $5")
st.caption("AI-powered penny stock + crypto day trading assistant")

# === User Inputs ===
market_type = st.selectbox("Choose Market", ["NYSE Penny Stocks", "Top Cryptos"])
buying_power = st.number_input("Your Buying Power ($)", value=50.0, min_value=1.0)
refresh_rate = st.selectbox("Refresh Rate", ["Manual", "Every 1 min", "Every 5 min"])
st.markdown("---")

# === Get NYSE Penny Stock Gainers ===
def get_nyse_gainers(limit=100):
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=sh_price_u5"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    df_list = pd.read_html(response.text)

    # Usually first or second table depending on layout
    for df in df_list:
        if "Ticker" in df.columns and "Price" in df.columns and "Change" in df.columns:
            break
    else:
        raise ValueError("Could not find the correct table format from Finviz")

    # Clean and rename columns
    df = df.rename(columns={
        "Ticker": "Ticker",
        "Company": "Name",
        "Price": "Price",
        "Change": "% Change",
        "Volume": "Volume"
    })

    # Ensure only relevant columns
    df = df[["Ticker", "Name", "Price", "% Change", "Volume"]]

    # Convert types safely
    df["% Change"] = pd.to_numeric(df["% Change"].astype(str).str.replace('%', ''), errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"].astype(str).str.replace('$', ''), errors="coerce")
    df["Volume"] = pd.to_numeric(df["Volume"].astype(str).str.replace(',', ''), errors="coerce")

    # Drop bad data
    df = df.dropna(subset=["Price", "% Change", "Volume"])

    # Sort
    df = df.sort_values(by="% Change", ascending=False)

    # Add shares to buy
    df["Shares to Buy"] = (buying_power / df["Price"]).fillna(0).astype(int)

    return df.head(limit)

# === Get Crypto Gainers ===
def get_top_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "percent_change_24h_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data)[["id", "symbol", "name", "current_price", "price_change_percentage_24h", "total_volume"]]
    df.columns = ["ID", "Symbol", "Name", "Price", "% Change", "Volume"]
    df["Shares to Buy"] = (buying_power / df["Price"]).fillna(0).astype(int)
    return df

# === Main Render ===
if market_type == "NYSE Penny Stocks":
    try:
        stock_data = get_nyse_gainers()
        st.dataframe(stock_data, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading NYSE gainers: {e}")

elif market_type == "Top Cryptos":
    try:
        crypto_data = get_top_cryptos()
        st.dataframe(crypto_data, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading crypto data: {e}")
