import yfinance as yf

def get_crypto_data(symbol, period='7d', interval='1h'):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period =period, interval = interval)
    return hist

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    price = ticker.info.get("regularMarketPrice", None)
    return price