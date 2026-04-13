import requests
import json

contracts = {
    "RiskRouter":          "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC",
    "ReputationRegistry":  "0x423a9904e39537a9997fbaF0f220d79D7d545763",
    "ValidationRegistry":  "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1",
    "AgentRegistry":       "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3",
}

# Try V2 API endpoint
ETHERSCAN_API = "https://api-sepolia.etherscan.io/v2/api"

for name, address in contracts.items():
    resp = requests.get(ETHERSCAN_API, params={
        "module": "contract",
        "action": "getabi",
        "address": address,
    })
    data = resp.json()
    if data["status"] == "1":
        print(f"\n{'='*60}")
        print(f"CONTRACT: {name} ({address})")
        print(f"{'='*60}")
        print(data["result"])
        
        # Save to file for later use
        filename = f"{name.lower()}_abi.json"
        with open(filename, "w") as f:
            f.write(data["result"])
        print(f"\n✅ Saved to {filename}")
    else:
        print(f"\n❌ {name}: {data['message']} — {data.get('result','')}")
