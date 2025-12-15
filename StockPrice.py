import os
import requests
from datetime import datetime

def read_watchlist(filename="watchlist.txt"):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found. Working dir is: {os.getcwd()}")

    symbols = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            symbol = line.strip().upper()
            if symbol:
                symbols.append(symbol)

    return symbols

def execution_logger(func):
    def wrapper(*args, **kwargs):
        # args = (self, symbol) for methods
        symbol = kwargs.get("symbol") or (args[1] if len(args) > 1 else "UNKNOWN")
        time_now = datetime.now().strftime("%H:%M:%S")
        print(f"[{time_now}] Fetching data for: {symbol}...")
        return func(*args, **kwargs)
    return wrapper

class StockClient:
    BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
    HEADERS = {"User-Agent": "Mozilla/5.0"}

    @execution_logger
    def fetch_price(self, symbol):
        url = self.BASE_URL.format(symbol=symbol)

        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()

            data = response.json()

            result = data.get("chart", {}).get("result")
            if not result:
                print(f"⚠️ No result for {symbol}. Possibly invalid symbol or blocked.")
                return None

            meta = result[0].get("meta", {})

            current_price = meta.get("regularMarketPrice")
            previous_close = meta.get("chartPreviousClose") or meta.get("previousClose")

            if current_price is None or previous_close is None:
                print(f" Missing fields for {symbol}.")
                return None

            return {
                "symbol": symbol,
                "current_price": current_price,
                "previous_close": previous_close
            }

        except Exception as e:
            print(f" Error fetching {symbol}: {e}")
            return None

if __name__ == "__main__":
    print("Working directory:", os.getcwd())

    symbols = read_watchlist()
    print("Symbols read:", symbols)

    client = StockClient()

    for sym in symbols:
        result = client.fetch_price(sym)
        print("Result:", result)
