# api.py

import requests
from typing import List, Dict, Union

BASE_URL = "https://api.coingecko.com/api/v3"

def get_top_coins(limit: int = 20, vs_currency: str = "usd") -> List[Dict]:
    """
    Fetches top cryptocurrencies by market capitalization.

    Args:
        limit (int): Number of coins to fetch.
        vs_currency (str): The fiat currency to display prices in.

    Returns:
        List of coin data dictionaries.
    """
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top coins: {e}")
        return []

def get_coin_market_chart(coin_id: str = "bitcoin", days: Union[int, str] = 2, vs_currency: str = "usd") -> Dict:
    """
    Fetches historical market chart data for a specific coin.

    Args:
        coin_id (str): The ID of the cryptocurrency.
        days (int | str): Number of days to fetch data for (e.g., 1, 7, 30).
        vs_currency (str): The fiat currency to display prices in.

    Returns:
        Dict with chart data (timestamps and prices).
    """
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": vs_currency,
        "days": days,
        "interval": "hourly"
    }
    try:
        response = requests.get(url, params=params)
        print(f"DEBUG URL: {response.url}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market chart for {coin_id}: {e}")
        return {}
