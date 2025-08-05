import pandas as pd

def market_chart_to_df(data: dict) -> pd.DataFrame:
    """
    Takes CoinGecko market_chart output and returns a DataFrame
    with datetime index, price, and volume columns.
    """
    prices = pd.DataFrame(data.get("prices", []), columns=["timestamp", "price"])
    volumes = pd.DataFrame(data.get("total_volumes", []), columns=["timestamp", "volume"])

    prices["timestamp"] = pd.to_datetime(prices["timestamp"], unit="ms")
    volumes["timestamp"] = pd.to_datetime(volumes["timestamp"], unit="ms")

    df = prices.set_index("timestamp").join(volumes.set_index("timestamp"))
    return df