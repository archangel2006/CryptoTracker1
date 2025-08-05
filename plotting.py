import pandas as pd
import plotly.express as px
from datetime import datetime

def plot_price_chart(market_data, coin_name="Bitcoin", currency="usd"):
    try:
        # Validate input
        if not market_data or "prices" not in market_data:
            raise ValueError("Invalid or empty market data")

        prices = market_data["prices"]  # list of [timestamp, price]

        # Convert to DataFrame
        df = pd.DataFrame(prices, columns=["timestamp", "price"])

        # Convert timestamp to readable datetime
        df["time"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Create Plotly line chart
        fig = px.line(
            df,
            x="time",
            y="price",
            title=f"{coin_name.capitalize()} Price Chart",
            labels={"time": "Time", "price": f"Price ({currency.upper()})"},
        )
        fig.update_layout(template="plotly_dark")  # Optional dark theme

        return fig

    except Exception as e:
        print(f"[Error] plot_price_chart(): {e}")
        return None
