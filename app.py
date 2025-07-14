import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Momentum Alpha 2.0", layout="wide")
st.title("🧠 Momentum Alpha — AI Stock Predictor")
st.caption("Enter any stock. Get live data + AI prediction on long/short/avoid.")

# --- Inputs ---
tickers = st.text_input("Enter stock tickers (comma-separated):", value="RELI, MSTY, CGTX").upper().replace(" ", "").split(",")
buying_power = st.number_input("Your buying power ($):", min_value=0.0, value=20.0)

# --- AI logic ---
def ai_trade_signal(price_change, volume):
    if price_change > 6 and volume > 500000:
        return "📈 LONG", 0.85
    elif price_change < -4 and volume > 500000:
        return "📉 SHORT", 0.80
    elif abs(price_change) < 1 and volume < 100000:
        return "⏳ AVOID", 0.60
    else:
        return "🤔 UNCLEAR", 0.50

# --- Fetch Data ---
@st.cache_data(ttl=60)
def fetch_data(tickers):
    data = yf.download(tickers, period="1d", interval="1m", group_by='ticker', threads=True)
    results = []

    for ticker in tickers:
        try:
            df = data[ticker]
            current_price = df['Close'].dropna().iloc[-1]
            open_price = df['Open'].dropna().iloc[0]
            volume = df['Volume'].dropna().iloc[-1]
            percent_change = ((current_price - open_price) / open_price) * 100
            shares = int(buying_power // current_price)
            signal, confidence = ai_trade_signal(percent_change, volume)

            results.append({
                "Ticker": ticker,
                "Price": round(current_price, 3),
                "% Change": round(percent_change, 2),
                "Volume": int(volume),
                "Shares to Buy": shares,
                "AI Signal": signal,
                "Confidence": f"{confidence:.0%}"
            })

        except Exception:
            results.append({
                "Ticker": ticker,
                "Price": "Error",
                "% Change": "Error",
                "Volume": "Error",
                "Shares to Buy": "N/A",
                "AI Signal": "N/A",
                "Confidence": "N/A"
            })

    return pd.DataFrame(results)

# --- Run ---
if st.button("Analyze"):
    df = fetch_data(tickers)
    df = df.sort_values(by="% Change", ascending=False)
    st.dataframe(df, use_container_width=True)
