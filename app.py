import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Momentum Alpha Scanner", layout="wide")

# === App Header ===
st.title("📈 Top 100 NYSE Penny Stock Gainers Under $5")
st.caption("AI-powered penny stock + crypto day trading assistant")

# === Sidebar Options ===
market = st.selectbox("Choose Market", ["NYSE Penny Stocks"])
buying_power = st.number_input("Your Buying Power ($)", min_value=0.0, value=50.0)
refresh_rate = st.selectbox("Refresh Rate", ["Manual", "Every 1 min", "Every 5 min"])

# === Function to get NYSE gainers ===
def get_nyse_gainers(limit=100):
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=sh_price_u5"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    tables = pd.read_html(response.text)

    # Find table with proper structure
    target_df = None
    for df in tables:
        cols = [col.lower() for col in df.columns.astype(str)]
        if "ticker" in cols and "price" in cols and "change" in cols:
            target_df = df
            break

    if target_df is None:
        raise ValueError("⚠️ Could not find stock data table. Finviz may have changed layout.")

    # Rename columns
    target_df = target_df.rename(columns={
        target_df.columns[0]: "Ticker",
        target_df.columns[1]: "Name",
        target_df.columns[2]: "Price",
        target_df.columns[3]: "% Change",
        target_df.columns[4]: "Volume"
    })

    # Clean numeric columns
    target_df["% Change"] = pd.to_numeric(
        target_df["% Change"].astype(str).str.replace('%', ''), errors="coerce")
    target_df["Price"] = pd.to_numeric(
        target_df["Price"].astype(str).str.replace('$', ''), errors="coerce")
    target_df["Volume"] = pd.to_numeric(
        target_df["Volume"].astype(str).str.replace(',', ''), errors="coerce")

    # Drop rows with bad data
    target_df = target_df.dropna(subset=["Price", "% Change", "Volume"])
    target_df = target_df.sort_values(by="% Change", ascending=False)

    # Calculate how many shares user could afford
    target_df["Shares to Buy"] = (buying_power / target_df["Price"]).fillna(0).astype(int)

    return target_df[["Ticker", "Name", "Price", "% Change", "Volume", "Shares to Buy"]].head(limit)

# === Display Data ===
if market == "NYSE Penny Stocks":
    try:
        df = get_nyse_gainers()
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading NYSE gainers: {e}")
