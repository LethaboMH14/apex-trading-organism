import requests
import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://ethereum-sepolia-rpc.publicnode.com"))
RISK_ROUTER = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"

# Fetch full ABI
resp = requests.get("https://eth-sepolia.blockscout.com/api", params={
    "module": "contract",
    "action": "getabi", 
    "address": RISK_ROUTER,
})
abi = resp.json()["result"]
abi_list = json.loads(abi)

print("=" * 80)
print("ALL RiskRouter functions:")
print("=" * 80)
for item in abi_list:
    if item.get("type") == "function":
        inputs = [(i["name"], i["type"]) for i in item.get("inputs", [])]
        outputs = [o['type'] for o in item.get('outputs', [])]
        mutability = item.get("stateMutability", "nonpayable")
        print(f"  {item['name']}({inputs}) → {outputs} [{mutability}]")

print("\n" + "=" * 80)
print("ALL RiskRouter events:")
print("=" * 80)
for item in abi_list:
    if item.get("type") == "event":
        inputs = [(i["name"], i["type"], i.get("indexed")) for i in item.get("inputs", [])]
        print(f"  {item['name']}({inputs})")

# Save ABI for later use
with open("riskrouter_full_abi.json", "w") as f:
    f.write(json.dumps(abi_list, indent=2))
print("\n✅ Saved full ABI to riskrouter_full_abi.json")
