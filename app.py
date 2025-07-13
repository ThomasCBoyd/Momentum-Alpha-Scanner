# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time

# === CONFIG ===
st.set_page_config(page_title="Momentum Alpha v2.5", layout="wide")
st.title("📈 Momentum Alpha Scanner v2.5")
st.caption("AI-powered penny stock + crypto day trading assistant")

# === USER INPUTS ===
market_type = st.selectbox("Choose Market", ["NYSE Penny Stocks", "Top Cryptos"])
buying_power = st.number_input("Your Buying Power ($)", value=20.0, min_value=1.0)
refresh_rate = st.selectbox("Refresh Rate", ["Manual", "Every 1 min", "Every 5 min"])

st.markdown("---")

# === DATA SOURCES ===

def get_nyse_gainers(limit=100):
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=sh_price_u5"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    df_list = pd.read_html(response.text)
    df = df_list[15]  # Main screener table

    df = df.rename(columns={
        "Ticker": "Ticker",
        "Company": "Name",
        "Price": "Price",
        "Change": "% Change",
        "Volume": "Volume"
    })

    df = df[['Ticker', 'Name', 'Price', '% Change', 'Volume']]

    # ✅ CLEANING FIX (safe for all characters)
    df['% Change'] = df['% Change'].astype(str).str.replace('%', '', regex=False).astype(float)
    df['Price'] = df['Price'].astype(str).str.replace(',', '').astype(float)
    df['Volume'] = df['Volume'].astype(str).str.replace(r'[^\d]', '', regex=True)
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0).astype(int)

    return df.head(limit)

def get_top_cryptos():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "percent_change_24h_desc",
        "per_page": 50,
        "page": 1
    }
    response = requests.get(url, params=params).json()
    df = pd.DataFrame(response)
    df = df[['symbol', 'name', 'current_price', 'price_change_percentage_24h', 'total_volume']]
    df.columns = ['Ticker', 'Name', 'Price', '% Change', 'Volume']
    df['Ticker'] = df['Ticker'].str.upper()
    df = df.sort_values(by='% Change', ascending=False)
    return df

def predict_trend(row):
    if row['% Change'] > 5 and row['Volume'] > 500000:
        return "📈 Bullish"
    elif row['% Change'] < -3:
        return "📉 Bearish"
    else:
        return "⏸️ Neutral"

def calculate_trade_setup(price):
    entry_low = price * 0.98
    entry_high = price * 1.01
    stop = price * 0.95
    target1 = price * 1.10
    target2 = price * 1.20
    rr_ratio = round((target1 - price) / (price - stop), 2)
    return entry_low, entry_high, stop, target1, target2, rr_ratio

def send_discord_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1394076725184299199/17ypxu1jBSY_DVLfKSPQTTnSRHv2Wp9s-Z1YtCmTuZC7pLLNHKRBJAJyzkZU3CrdQYX5"
    data = {"content": message}
    requests.post(webhook_url, json=data)

# === REFRESH TIMER ===
if refresh_rate == "Every 1 min":
    time.sleep(60)
elif refresh_rate == "Every 5 min":
    time.sleep(300)

# === LOAD DATA ===
if market_type == "NYSE Penny Stocks":
    st.subheader("📊 Top 100 NYSE Penny Stock Gainers Under $5")
    data = get_nyse_gainers()
else:
    st.subheader("📊 Top Cryptos by 24H % Change")
    data = get_top_cryptos()

# === AI ANALYSIS ===
data['Trend'] = data.apply(predict_trend, axis=1)
data['Entry Zone'] = data['Price'].apply(lambda x: f"${x*0.98:.2f} - ${x*1.01:.2f}")
data['Stop Loss'] = data['Price'].apply(lambda x: f"${x*0.95:.2f}")
data['Target'] = data['Price'].apply(lambda x: f"${x*1.10:.2f} / ${x*1.20:.2f}")
data['Shares to Buy'] = (buying_power / data['Price']).astype(int)
data['R/R'] = data['Price'].apply(lambda x: round((x*1.10 - x) / (x - x*0.95), 2))

st.dataframe(data[['Ticker', 'Price', '% Change', 'Volume', 'Trend', 'Entry Zone', 'Stop Loss', 'Target', 'R/R', 'Shares to Buy']].head(20), use_container_width=True)

# === DISCORD ALERTS ===
st.markdown("## 🔔 Live AI Trade Alerts")
for idx, row in data.iterrows():
    if row['Trend'] == "📈 Bullish" and row['% Change'] > 5:
        alert = (
            f"📢 **BUY SIGNAL: {row['Ticker']}**\n"
            f"Price: ${row['Price']:.2f} | Entry: {row['Entry Zone']} | Stop: {row['Stop Loss']}\n"
            f"Target: {row['Target']} | Trend: {row['Trend']} | R/R: {row['R/R']}\n"
            f"✅ Buy {row['Shares to Buy']} shares w/ ${buying_power} buying power"
        )
        send_discord_alert(alert)
        st.success(f"Alert sent for {row['Ticker']}")

# === TRADE JOURNAL ===
st.markdown("## 📒 Trade Log (Manual Entry for Now)")

if 'trades' not in st.session_state:
    st.session_state.trades = []

with st.form("log_trade"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        trade_ticker = st.text_input("Ticker")
    with col2:
        entry_price = st.number_input("Entry Price", value=0.0)
    with col3:
        exit_price = st.number_input("Exit Price", value=0.0)
    with col4:
        quantity = st.number_input("Shares", value=1, min_value=1)

    submitted = st.form_submit_button("Log Trade")
    if submitted:
        profit = round((exit_price - entry_price) * quantity, 2)
        st.session_state.trades.append({
            "Ticker": trade_ticker.upper(),
            "Entry": entry_price,
            "Exit": exit_price,
            "Shares": quantity,
            "P/L": profit
        })

if st.session_state.trades:
    trade_df = pd.DataFrame(st.session_state.trades)
    st.dataframe(trade_df, use_container_width=True)
    csv = trade_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Trade Log", data=csv, file_name="trade_log.csv", mime="text/csv")

st.markdown("---")
st.caption("🧠 Built by Thomas Boyd | Momentum Alpha Scanner v2.5")
