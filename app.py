import streamlit as st
import pandas as pd
from yahoo_fin import stock_info as si
from requests_html import HTMLSession

# -----------------------------
# Setup: Streamlit UI
# -----------------------------
st.set_page_config(page_title="Momentum Alpha", layout="wide")

st.title("📈 Top 100 NYSE Penny Stock Gainers Under $5")
st.caption("AI-powered penny stock + crypto day trading assistant")

market = st.selectbox("Choose Market", ["NYSE Penny Stocks", "Crypto"], index=0)
buying_power = st.number_input("Your Buying Power ($)", min_value=0.0, value=50.0)
refresh_rate = st.selectbox("Refresh Rate", ["Manual", "Every 1 min", "Every 5 min"], index=0)

st.divider()

# -----------------------------
# Scraper Function: NYSE Gainers Under $5
# -----------------------------
def get_nyse_gainers():
    try:
        url = "https://finance.yahoo.com/screener/predefined/day_gainers"
        session = HTMLSession()
        r = session.get(url)
        r.html.render(sleep=2, timeout=20)
        table = r.html.find("table", first=True)
        rows = table.find("tr")[1:]  # Skip header

        data = []
        for row in rows:
            cols = row.find("td")
            if len(cols) >= 6:
                ticker = cols[0].text
                name = cols[1].text
                price = float(cols[2].text.replace(",", "").replace("$", ""))
                change_pct = float(cols[4].text.replace("%", "").replace("+", "").replace(",", ""))
                volume_str = cols[5].text.replace(",", "").replace("M", "e6").replace("K", "e3")
                try:
                    volume = float(eval(volume_str))
                except:
                    volume = 0

                if price < 5.00:
                    data.append({
                        "Ticker": ticker,
                        "Name": name,
                        "Price": price,
                        "% Change": change_pct,
                        "Volume": volume
                    })

        df = pd.DataFrame(data)
        df.sort_values(by="% Change", ascending=False, inplace=True)
        return df

    except Exception as e:
        st.error(f"Error loading NYSE gainers: {e}")
        return pd.DataFrame()

# -----------------------------
# Main Logic
# -----------------------------
if market == "NYSE Penny Stocks":
    df = get_nyse_gainers()

    if not df.empty:
        try:
            df["Shares to Buy"] = (buying_power / df["Price"]).astype(int)
            st.dataframe(df[["Ticker", "Name", "Price", "% Change", "Volume", "Shares to Buy"]], use_container_width=True)
        except Exception as e:
            st.error(f"Error calculating shares to buy: {e}")
    else:
        st.warning("No penny stock gainers found under $5.")

elif market == "Crypto":
    st.warning("Crypto scanning is coming soon!")
