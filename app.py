import streamlit as st
import pandas as pd
import requests

# === PAGE CONFIG ===
st.set_page_config(page_title="Momentum Alpha v2.5+", layout="wide")
st.title("📈 Momentum Alpha Scanner v2.5+")
st.caption("AI-powered penny stock + crypto day trading assistant")

# === USER INPUTS ===
market_type = st.selectbox("Choose Market:", ["NYSE Penny Stocks", "Top Cryptos"])
buying_power = st.number_input("Your Buying Power ($)", value=20.0, min_value=1.0)
refresh_rate = st.selectbox("Refresh Rate:", ["Manual", "Every 1 min", "Every 5 min"])

st.markdown("---")

# === NYSE PENNY STOCKS ===
def get_nyse_gainers(limit=100):
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=sh_price_u5"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    df_list = pd.read_html(response.text)

    if len(df_list) > 0:
        df = df_list[0]
        df = df.rename(columns={
            "Ticker": "Ticker",
            "Company": "Name",
            "Price": "Price",
            "Change": "% Change",
            "Volume": "Volume"
        })

        df = df[["Ticker", "Name", "Price", "% Change", "Volume"]]
        df = df.head(limit)

        # Clean and convert
        df = df.dropna(subset=["Price", "% Change", "Volume"])
        df["Price"] = df["Price"].astype(str).str.replace("$", "").str.replace(",", "").astype(float)
        df["% Change"] = df["% Change"].astype(str).str.replace("%", "").str.replace(",", "").astype(float)
        df["Volume"] = df["Volume"].astype(str).str.replace(",", "").str.replace("K", "e3").str.replace("M", "e6")
        df["Volume"] = df["Volume"].apply(pd.eval).astype(int)

        df = df[df["Price"] > 0]
        df["Shares to Buy"] = (buying_power / df["Price"]).fillna(0).astype(int)

        return df

    return pd.DataFrame(columns=["Ticker", "Name", "Price", "% Change", "Volume", "Shares to Buy"])

# === TOP CRYPTOS ===
def get_top_cryptos(limit=100):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "percent_change_24h_desc", "per_page": limit, "page": 1}
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data)[["symbol", "name", "current_price", "price_change_percentage_24h", "total_volume"]]
    df.columns = ["Ticker", "Name", "Price", "% Change", "Volume"]

    df = df.dropna(subset=["Price", "% Change", "Volume"])
    df = df[df["Price"] > 0]
    df["Price"] = df["Price"].astype(float)
    df["% Change"] = df["% Change"].astype(float)
    df["Volume"] = df["Volume"].astype(float).astype(int)

    df["Shares to Buy"] = (buying_power / df["Price"]).fillna(0).astype(int)
    return df

# === DISPLAY OUTPUT ===
if market_type == "NYSE Penny Stocks":
    st.subheader("📊 Top 100 NYSE Penny Stock Gainers Under $5")
    data = get_nyse_gainers()
else:
    st.subheader("💎 Top 100 Crypto Gainers (24h)")
    data = get_top_cryptos()

st.dataframe(data, use_container_width=True)
