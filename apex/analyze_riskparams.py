import requests
import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://ethereum-sepolia-rpc.publicnode.com"))
RISK_ROUTER = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"

# Load ABI
with open("riskrouter_full_abi.json", "r") as f:
    abi_list = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(RISK_ROUTER), 
    abi=abi_list
)

print("=" * 80)
print("STEP 3: riskParams field names and values")
print("=" * 80)

# Find riskParams function and call it with named outputs
risk_fn = next(f for f in abi_list 
               if f.get("name") == "riskParams" and f.get("type") == "function")
print("riskParams outputs:", [(o["name"], o["type"]) for o in risk_fn.get("outputs", [])])

result = contract.functions.riskParams(26).call()
outputs = risk_fn.get("outputs", [])
for i, val in enumerate(result):
    name = outputs[i]["name"] if i < len(outputs) else f"field_{i}"
    print(f"  {name}: {val}")

print("\n" + "=" * 80)
print("STEP 4: getTradeRecord field names")
print("=" * 80)

trade_fn = next(f for f in abi_list 
                if f.get("name") == "getTradeRecord" and f.get("type") == "function")
print("getTradeRecord outputs:", [(o["name"], o["type"]) for o in trade_fn.get("outputs", [])])

result = contract.functions.getTradeRecord(26).call()
outputs = trade_fn.get("outputs", [])
for i, val in enumerate(result):
    name = outputs[i]["name"] if i < len(outputs) else f"field_{i}"
    print(f"  {name}: {val}")

print("\n" + "=" * 80)
