# app.py

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Crypto Tracker", layout="wide")

# Title
st.title("💰 Crypto Tracker")

# API endpoints
COIN_LIST_URL = "https://api.coingecko.com/api/v3/coins/list"
MARKET_DATA_URL = "https://api.coingecko.com/api/v3/coins/{id}"
MARKET_CHART_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

# Helper: fetch list of coins
@st.cache_data
def get_coin_list():
    try:
        response = requests.get(COIN_LIST_URL)
        response.raise_for_status()
        coins = response.json()
        return {coin["name"]: coin["id"] for coin in coins}
    except Exception as e:
        st.error(f"Failed to fetch coin list: {e}")
        return {}

# Helper: fetch market data
def get_market_data(coin_id, vs_currency):
    try:
        url = MARKET_DATA_URL.format(id=coin_id)
        params = {"localization": "false", "tickers": "false", "market_data": "true"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        market_data = data.get("market_data", {})
        return {
            "current_price": market_data["current_price"].get(vs_currency),
            "price_change_24h": market_data["price_change_percentage_24h"],
            "market_cap": market_data["market_cap"].get(vs_currency),
        }
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return None

# Helper: fetch price chart data
def get_price_chart_data(coin_id, vs_currency, days):
    try:
        url = MARKET_CHART_URL.format(id=coin_id)
        params = {"vs_currency": vs_currency, "days": days}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df[["date", "price"]]
    except Exception as e:
        st.error(f"Error fetching price chart: {e}")
        return pd.DataFrame()

# Sidebar controls
st.sidebar.header("Settings")

coin_dict = get_coin_list()
if not coin_dict:
    st.stop()

coin_name = st.sidebar.selectbox("Select Cryptocurrency", list(coin_dict.keys()))
coin_id = coin_dict[coin_name]

currency = st.sidebar.selectbox("Currency", ["usd", "inr", "eur"])
chart_days = st.sidebar.selectbox("Chart Duration", ["1", "7", "30", "90"], format_func=lambda x: f"{x} days")

# Show loading spinner while fetching
with st.spinner("Fetching data..."):
    market_info = get_market_data(coin_id, currency)
    df_price = get_price_chart_data(coin_id, currency, "2" if chart_days == "1" else chart_days)

# Display stats
if market_info:
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"{market_info['current_price']:.2f} {currency.upper()}")
    col2.metric("24h Change", f"{market_info['price_change_24h']:.2f} %")
    col3.metric("Market Cap", f"{market_info['market_cap']:,} {currency.upper()}")

# Display chart
if not df_price.empty:
    st.subheader(f"{coin_name} Price Chart ({chart_days} days)")
    fig = px.line(df_price, x="date", y="price", title=f"{coin_name} to {currency.upper()} Price", template="plotly_dark")
    fig.update_layout(xaxis_title="Date", yaxis_title=f"Price ({currency.upper()})")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No price data available.")
