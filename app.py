import streamlit as st
import pandas as pd
import requests

# === CONFIG ===
st.set_page_config(page_title="Momentum Alpha v2.5+", layout="wide")
st.title("📈 Top 100 NYSE Penny Stock Gainers Under $5")
st.caption("AI-powered penny stock + crypto day trading assistant")

# === USER INPUTS ===
market_type = st.selectbox("Choose Market", ["NYSE Penny Stocks", "Top Cryptos"])
buying_power = st.number_input("Your Buying Power ($)", value=20.0, min_value=1.0)
refresh_rate = st.selectbox("Refresh Rate", ["Manual", "Every 1 min", "Every 5 min"])

st.markdown("---")


# === DATA SOURCE: NYSE PENNY STOCK GAINERS ===
def get_nyse_gainers(limit=100):
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=sh_price_u5"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    df_list = pd.read_html(response.text)

    # Table 1 is the correct result
    df = df_list[0]

    # Rename & select only needed columns
    df = df.rename(columns={
        "Ticker": "Ticker",
        "Company": "Name",
        "Price": "Price",
        "Change": "% Change",
        "Volume": "Volume"
    })

    df = df[["Ticker", "Name", "Price", "% Change", "Volume"]]

    # Convert data safely
    df["% Change"] = pd.to_numeric(
        df["% Change"].astype(str).str.replace('%', '', regex=False),
        errors="coerce"
    )

    df["Price"] = pd.to_numeric(
        df["Price"].astype(str).str.replace('$', '', regex=False),
        errors="coerce"
    )

    df["Volume"] = pd.to_numeric(
        df["Volume"].astype(str).str.replace(',', '', regex=False),
        errors="coerce"
    )

    # Drop rows with bad data
    df = df.dropna(subset=["Price", "% Change", "Volume"])

    # Sort by % Change descending
    df = df.sort_values(by="% Change", ascending=False)

    # Calculate shares to buy
    df["Shares to Buy"] = (buying_power / df["Price"]).fillna(0).astype(int)

    return df.head(limit)


# === DATA SOURCE: TOP CRYPTOS (OPTIONAL FUTURE) ===
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


# === MAIN RENDER ===
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
