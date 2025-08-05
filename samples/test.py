from api import get_coin_market_chart
from plotting import plot_price_chart
import streamlit as st

market_data = get_coin_market_chart("bitcoin", 1)
fig = plot_price_chart(market_data, "bitcoin", "usd")

if fig:
    st.plotly_chart(fig)
else:
    st.error("Failed to generate price chart.")
