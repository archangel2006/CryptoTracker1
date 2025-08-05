# app.py

import streamlit as st
from api import get_top_coins, get_coin_market_chart
from plotting import plot_price_chart

st.set_page_config(page_title="Crypto Tracker", layout="wide")
st.title("💰 Real-Time Crypto Tracker")

# --- Sidebar Inputs ---
st.sidebar.header("Customize View")

# Currency Selection
vs_currency = st.sidebar.selectbox("Select Currency", ["usd", "inr", "eur", "gbp"])

# Number of Top Coins
limit = st.sidebar.slider("Number of Top Coins", min_value=5, max_value=50, value=20)

# Time Duration
days = st.sidebar.selectbox("Time Duration (days)", [1, 7, 30, 90, 180, 365, "max"])
days = str(days)  # convert to string for API

# Get top coins list (for coin dropdown)
top_coins = get_top_coins(limit=limit, vs_currency=vs_currency)

coin_options = {coin["name"]: coin["id"] for coin in top_coins}
coin_name = st.sidebar.selectbox("Select Coin", list(coin_options.keys()))
coin_id = coin_options[coin_name]

# --- Main Content ---

st.subheader(f"📈 {coin_name} Price Chart ({vs_currency.upper()}, Last {days} days)")

# Fetch and plot market data
market_data = get_coin_market_chart(coin_id=coin_id, days=days, vs_currency=vs_currency)
st.write("DEBUG: market_data", market_data)  # 🐛 shows data in Streamlit
fig = plot_price_chart(market_data, coin_name=coin_name)

if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Failed to load chart. Please try again.")

# Display top coins table
st.subheader(f"🏆 Top {limit} Coins by Market Cap ({vs_currency.upper()})")
if top_coins:
    display_data = [
        {
            "Name": coin["name"],
            "Symbol": coin["symbol"].upper(),
            "Price": f'{coin["current_price"]} {vs_currency.upper()}',
            "24h Change (%)": round(coin["price_change_percentage_24h"], 2),
            "Market Cap": f'{coin["market_cap"]:,}'
        }
        for coin in top_coins
    ]
    st.dataframe(display_data)
else:
    st.warning("Could not fetch top coins.")
    
