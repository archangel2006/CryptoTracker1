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
CURRENCY_LIST_URL = "https://api.coingecko.com/api/v3/simple/supported_vs_currencies"
MARKET_DATA_URL = "https://api.coingecko.com/api/v3/coins/{id}"
MARKET_CHART_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

# Currency symbol map (partial, optional)
currency_symbols = {
    "usd": "$", "inr": "₹", "eur": "€", "jpy": "¥", "gbp": "£",
    "aud": "A$", "cad": "C$", "cny": "¥", "krw": "₩", "rub": "₽", "brl": "R$",
}

# Helper: fetch coin list
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

# Helper: fetch supported currencies
@st.cache_data
def get_supported_currencies():
    try:
        response = requests.get(CURRENCY_LIST_URL)
        response.raise_for_status()
        return sorted(response.json())
    except Exception as e:
        st.error(f"Failed to fetch currency list: {e}")
        return ["usd", "inr", "eur"]

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

# Helper: fetch chart data
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

# Sidebar
st.sidebar.header("Settings")

coin_dict = get_coin_list()
if not coin_dict:
    st.stop()

currencies = get_supported_currencies()
coin_name = st.sidebar.selectbox("Select Cryptocurrency", list(coin_dict.keys()))
currency = st.sidebar.selectbox("Currency", currencies, index=currencies.index("usd") if "usd" in currencies else 0)
chart_days = st.sidebar.selectbox("Chart Duration", ["1", "7", "30", "90"], format_func=lambda x: f"{x} days")

coin_id = coin_dict[coin_name]
currency_symbol = currency_symbols.get(currency, currency.upper())

# Load data
with st.spinner("Fetching data..."):
    market_info = get_market_data(coin_id, currency)
    df_price = get_price_chart_data(coin_id, currency, "2" if chart_days == "1" else chart_days)

# Display metrics
if market_info:
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"{currency_symbol} {market_info['current_price']:.2f}")
    col2.metric("24h Change", f"{market_info['price_change_24h']:.2f} %")
    col3.metric("Market Cap", f"{currency_symbol} {market_info['market_cap']:,}")
else:
    st.warning("No market data available.")

# Display chart
if not df_price.empty:
    st.subheader(f"{coin_name} Price Chart ({chart_days} days)")
    fig = px.line(df_price, x="date", y="price",
                  title=f"{coin_name} to {currency.upper()} Price",
                  template="plotly_dark")
    fig.update_layout(xaxis_title="Date", yaxis_title=f"Price ({currency_symbol})")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No price data available.")
