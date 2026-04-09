import os
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('../.env.local')
from kraken_live import KrakenLiveTrader

print("Testing Kraken CLI integration...")
k = KrakenLiveTrader()
ok, version = k.test_connection()
print('CLI connected:', ok)
print('Version:', version)
bal = k.get_balance()
print('Balance:', bal)
