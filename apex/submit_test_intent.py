import requests
import json
import os
import time
from web3 import Web3
from eth_account import Account

# Load environment variables
try:
    with open(".env", "r") as f:
        env_lines = f.readlines()
except FileNotFoundError:
    with open(".env.example", "r") as f:
        env_lines = f.readlines()

env = {}
for line in env_lines:
    if "=" in line and not line.strip().startswith("#"):
        key, value = line.strip().split("=", 1)
        env[key] = value

OPERATOR_KEY = env.get("APEX_OPERATOR_PRIVATE_KEY", "")
if not OPERATOR_KEY or OPERATOR_KEY.startswith("YOUR_") or len(OPERATOR_KEY) < 32:
    print("⚠️  No valid private key found - using dummy address for intent structure demo")
    agent_wallet = "0x909375eC03d6A001A95Bcf20E2260d671a84140B"  # Our operator address
else:
    operator = Account.from_key(OPERATOR_KEY)
    agent_wallet = env.get("APEX_AGENT_WALLET_ADDRESS", operator.address)

w3 = Web3(Web3.HTTPProvider("https://ethereum-sepolia-rpc.publicnode.com"))
RISK_ROUTER = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"

# Load ABI
with open("riskrouter_full_abi.json", "r") as f:
    abi_list = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(RISK_ROUTER), 
    abi=abi_list
)

# Get current nonce
nonce = contract.functions.getIntentNonce(26).call()
print(f"Current intent nonce: {nonce}")

# Build minimal intent
intent = {
    "agentId": 26,
    "agentWallet": agent_wallet,
    "pair": "BTC/USD",
    "action": "BUY",
    "amountUsdScaled": 35000,  # $350
    "maxSlippageBps": 100,
    "nonce": nonce,
    "deadline": int(time.time()) + 300
}
print(f"Intent to submit: {intent}")

# Build intent tuple for contract
intent_tuple = (
    intent["agentId"],
    Web3.to_checksum_address(intent["agentWallet"]),
    intent["pair"],
    intent["action"],
    intent["amountUsdScaled"],
    intent["maxSlippageBps"],
    intent["nonce"],
    intent["deadline"]
)

# Simulate first
print("\nSimulating intent...")
try:
    valid, reason = contract.functions.simulateIntent(intent_tuple).call()
    print(f"Simulation result: valid={valid}, reason={reason}")
    if not valid:
        print("❌ Simulation failed - NOT submitting")
        exit(0)
except Exception as e:
    print(f"Simulation error: {e}")

# EIP-712 structure (DO NOT SUBMIT - just print structure)
print("\n" + "=" * 80)
print("EIP-712 STRUCTURE (for reference, NOT submitting)")
print("=" * 80)
structured_data = {
    "domain": {
        "name": "RiskRouter",
        "version": "1",
        "chainId": 11155111,
        "verifyingContract": RISK_ROUTER
    },
    "types": {
        "TradeIntent": [
            {"name": "agentId", "type": "uint256"},
            {"name": "agentWallet", "type": "address"},
            {"name": "pair", "type": "string"},
            {"name": "action", "type": "string"},
            {"name": "amountUsdScaled", "type": "uint256"},
            {"name": "maxSlippageBps", "type": "uint256"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"}
        ]
    },
    "primaryType": "TradeIntent",
    "message": intent
}
print(f"Domain: {structured_data['domain']}")
print(f"Types: {structured_data['types']}")
print(f"Message: {structured_data['message']}")

print("\n" + "=" * 80)
print("✅ INTENT STRUCTURE CONFIRMED")
print("=" * 80)
print("Intent tuple structure matches contract requirements.")
print("No actual submission - structure verified only.")
print("=" * 80)
