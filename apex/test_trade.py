from kraken_live import KrakenLiveTrader
import os
from dotenv import load_dotenv

load_dotenv('../.env.local')

print("Testing Kraken trade execution...")
k = KrakenLiveTrader()

# Test with very small amount
result = k.place_market_order("BTCUSD", "buy", 0.001)
print("Order result:", result)
