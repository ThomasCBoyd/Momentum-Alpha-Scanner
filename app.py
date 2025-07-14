import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# CONFIG
st.set_page_config(page_title="Momentum Alpha", layout="wide")
st.title("🚀 Momentum Alpha — Penny Stock AI Scanner")
st.caption("Live penny stock scanner + buy alerts — works on mobile")

# Ticker Input
tickers = st.text_input(
    "Enter penny stock tickers (comma-separated):",
    value="RELI, CGTX, MSTY, PTLE, BLDE, AVTX, BNGO"
).upper().replace(" ", "").split(",")

# Buying power input
buying_power = st.number_input("Your Buying Power ($):", min_value=0.0, value=20.0)

# Refresh rate
refresh_rate = st.selectbox("Auto-refresh every:", ["Manual", "60 seconds", "300 seconds"])

# Discord webhook
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1394076725184299199/17ypxu1jBSY_DVLfKSPQTTnSRHv2Wp9s-Z1YtCmTuZC7pLLNHKRBJAJyzkZU3CrdQYX5"

@st.cache_data(ttl=60)
def get_stock_data(tickers):
    data = yf.download(tickers, period="1d", interval="1m", group_by='ticker', threads=True)
    results = []
    alerts = []

    for ticker in tickers:
        try:
            df = data[ticker]
            current_price = df['Close'].dropna().iloc[-1]
            open_price = df['Open'].dropna().iloc[0]
            percent_change = ((current_price - open_price) / open_price) * 100
            volume = df['Volume'].dropna().iloc[-1]
            shares = int(buying_power // current_price)

            # AI-lite breakout logic
            if percent_change > 7 and volume > 500000:
                alert = f"🚨 {ticker} is up {percent_change:.2f}% with strong volume ({int(volume)})."
                send_discord_alert(alert)
                alerts.append(alert)

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

    return pd.DataFrame(results), alerts

def send_discord_alert(message):
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except:
        pass

# Fetch + Display
if st.button("Scan Now") or refresh_rate != "Manual":
    data, alerts = get_stock_data(tickers)
    data = data.sort_values(by="% Change", ascending=False)
    st.dataframe(data, use_container_width=True)
    if alerts:
        st.warning("Alerts sent to Discord!")
    if refresh_rate != "Manual":
        time.sleep(60 if refresh_rate == "60 seconds" else 300)
        st.rerun()
