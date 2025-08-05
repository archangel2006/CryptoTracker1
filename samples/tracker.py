import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Streamlit page configuration
st.set_page_config(
    page_title="Crypto Tracker",
    layout="wide",
)

st.title("🔍 Crypto Tracker")
st.markdown("Track live prices, 24h change, market cap, and historical charts for any cryptocurrency.")

# Sidebar controls
st.sidebar.header("Settings")

# Dark mode toggle for chart
dark_mode = st.sidebar.checkbox("Dark Mode for Chart", value=False)

# 1. Fetch list of all coins
with st.spinner("Loading cryptocurrency list..."):
    try:
        coins_resp = requests.get("https://api.coingecko.com/api/v3/coins/list", timeout=10)
        coins_resp.raise_for_status()
        coins = coins_resp.json()
    except Exception as e:
        st.error(f"Failed to fetch coin list: {e}")
        st.stop()

# Build display map: "Name (SYMBOL)" -> id
coin_display_map = {
    f"{coin['name']} ({coin['symbol'].upper()})": coin["id"]
    for coin in coins
}

# 2. User selections
coin_choice = st.sidebar.selectbox(
    "Select Cryptocurrency",
    options=sorted(coin_display_map.keys())
)
coin_id = coin_display_map[coin_choice]

currency = st.sidebar.selectbox(
    "Select Currency",
    options=["USD", "INR", "EUR"],
    index=0
)

duration_map = {
    "24 Hours": 1,
    "7 Days": 7,
    "30 Days": 30,
    "90 Days": 90,
}
duration_label = st.sidebar.selectbox(
    "Chart Duration",
    options=list(duration_map.keys()),
    index=1
)
days = duration_map[duration_label]

# 3. Fetch current price & metrics
with st.spinner("Fetching market data..."):
    try:
        price_resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": currency.lower(),
                "include_24hr_change": "true",
                "include_market_cap": "true",
            },
            timeout=10,
        )
        price_resp.raise_for_status()
        price_data = price_resp.json()[coin_id]
        
        current_price = price_data[currency.lower()]
        change_24h = price_data[f"{currency.lower()}_24h_change"]
        market_cap = price_data[f"{currency.lower()}_market_cap"]
    except Exception as e:
        st.error(f"Failed to fetch price data: {e}")
        st.stop()

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric(
    label="Current Price",
    value=f"{currency} {current_price:,.2f}",
    delta=f"{change_24h:+.2f}%",
)
col2.metric(label="24h Change", value=f"{change_24h:+.2f}%")
col3.metric(label="Market Cap", value=f"{currency} {market_cap:,.0f}")

st.markdown("---")

# 4. Fetch historical price data
#    For 1-day charts, request 2 days of data to get hourly granularity
days_param = 2 if days == 1 else days

with st.spinner("Loading historical price data..."):
    try:
        chart_resp = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            params={
                "vs_currency": currency.lower(),
                "days": days_param,
            },
            timeout=10,
        )
        chart_resp.raise_for_status()
        chart_json = chart_resp.json()
    except Exception as e:
        st.error(f"Failed to fetch historical data: {e}")
        st.stop()

# Prepare DataFrame
prices = chart_json.get("prices", [])
df = pd.DataFrame(prices, columns=["timestamp", "price"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

# If user wants a 24-hour chart, trim to last 24h
if days == 1:
    cutoff = df["timestamp"].max() - pd.Timedelta(days=1)
    df = df[df["timestamp"] >= cutoff]

# 5. Plot interactive chart
template = "plotly_dark" if dark_mode else "plotly_white"
fig = px.line(
    df,
    x="timestamp",
    y="price",
    title=f"{coin_choice} Price over the Last {duration_label}",
    labels={"timestamp": "Time", "price": f"Price ({currency})"},
    template=template,
)
fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))

st.plotly_chart(fig, use_container_width=True)