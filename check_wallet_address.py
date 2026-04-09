#!/usr/bin/env python3
"""Check which address is derived from the private key in .env"""
import os
from eth_account import Account

# Load the private key from .env
APEX_PRIVATE_KEY = "077f5f7d6b70a90a9d4eba43a003b565cc26d85fc8724f452d08176633f9ea28"

# Derive the address
account = Account.from_key(APEX_PRIVATE_KEY)
derived_address = account.address

print(f"Private Key (first 6 chars): {APEX_PRIVATE_KEY[:6]}...{APEX_PRIVATE_KEY[-4:]}")
print(f"Derived Address: {derived_address}")
print(f"Expected Whitelisted Address: 0x909375eC03d6A001A95Bcf20E2260d671a84140B")
print(f"Match: {derived_address.lower() == '0x909375eC03d6A001A95Bcf20E2260d671a84140B'.lower()}")
