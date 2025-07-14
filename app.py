import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Momentum Alpha Scanner", layout="wide")
st.title("📈 Top 100 NYSE Penny Stock Gainers Under $5")
st.caption("AI-powered penny stock + crypto day trading assistant")

market = st.selectbox("Choose Market", ["NYSE Penny Stocks"])
buying_power = st.number_input("Your Buying Power ($)", min_value=0.0, value=50.0)
refresh_rate = st.selectbox("Refresh Rate", ["Manual", "Every 1 min", "Every 5 min"])

def get_robinhood_top_movers(limit=100):
    url = "https://api.robinhood.com/midlands/marketdata/instruments/top-movers/"
    params = {
        "direction": "up",
        "limit": limit,
        "type": "equity"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        records = []
        for stock in data.get("results", []):
            try:
                price = float(stock["last_trade_price"])
                if price <= 5.00:  # filter under $5
                    records.append({
                        "Ticker": stock["symbol"],
                        "Name": stock["simple_name"] or stock["name"],
                        "Price": price,
                        "% Change": round(float(stock["previous_close_price"]) and ((price - float(stock["previous_close_price"])) / float(stock["previous_close_price"])) * 100, 2),
                        "Shares to Buy": int(buying_power // price),
                    })
            except:
                continue

        return pd.DataFrame(records)

    except Exception as e:
        raise RuntimeError(f"Robinhood API error: {e}")

# === Display
if market == "NYSE Penny Stocks":
    try:
        df = get_robinhood_top_movers()
        if df.empty:
            st.warning("No gainers under $5 found right now.")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading NYSE gainers: {e}")
