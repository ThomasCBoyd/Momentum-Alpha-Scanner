import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Momentum Alpha v2.5", layout="wide")
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton > button { background-color: #04AA6D; color: white; }
    .stTextInput > div > input { background-color: #1e222c; color: white; }
    .stNumberInput > div > input { background-color: #1e222c; color: white; }
    .metric { padding: 8px; border-radius: 6px; background-color: #1c1f26; margin-bottom: 8px; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🚀 Momentum Alpha")
st.subheader("AI-Powered Penny Stock Predictor")

# --- User Input ---
tickers = st.text_input("🔍 Enter Tickers (e.g. RELI, MSTY, CGTX):", value="RELI, MSTY, CGTX").upper().replace(" ", "").split(",")
buying_power = st.number_input("💵 Buying Power ($)", min_value=0.0, value=20.0)

# --- AI logic ---
def ai_trade_signal(price_change, volume):
    if price_change > 6 and volume > 500000:
        return "📈 LONG", 0.85, "#10c469"
    elif price_change < -4 and volume > 500000:
        return "📉 SHORT", 0.80, "#ff5b5b"
    elif abs(price_change) < 1 and volume < 100000:
        return "⏳ AVOID", 0.60, "#cccccc"
    else:
        return "🤔 UNCLEAR", 0.50, "#ffaa00"

# --- Stock Fetch ---
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

            signal, confidence, color = ai_trade_signal(percent_change, volume)

            results.append({
                "Ticker": ticker,
                "Price": round(current_price, 3),
                "% Change": round(percent_change, 2),
                "Volume": int(volume),
                "Shares": shares,
                "Signal": signal,
                "Confidence": f"{confidence:.0%}",
                "Color": color
            })

        except:
            results.append({
                "Ticker": ticker,
                "Price": "Error",
                "% Change": "Error",
                "Volume": "Error",
                "Shares": "N/A",
                "Signal": "N/A",
                "Confidence": "N/A",
                "Color": "#666666"
            })

    return pd.DataFrame(results)

# --- Display Results ---
if st.button("🚀 Analyze Now"):
    df = fetch_data(tickers)
    for i, row in df.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div class='metric'>
                    <strong style='font-size: 20px;'>{row['Ticker']}</strong><br>
                    💵 <strong>${row['Price']}</strong> | 📊 <span style='color: {"#10c469" if row["% Change"] != "Error" and float(row["% Change"]) > 0 else "#ff5b5b"}'>{row['% Change']}%</span> | 📦 Volume: {row['Volume']}<br>
                    🧮 Shares to Buy: {row['Shares']}<br>
                    <span style='color: {row["Color"]}; font-weight: bold;'>{row['Signal']} (Confidence: {row['Confidence']})</span>
                </div>
                """,
                unsafe_allow_html=True
            )
