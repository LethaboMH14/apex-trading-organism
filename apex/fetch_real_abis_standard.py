import requests
import json

contracts = {
    "RiskRouter":          "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC",
    "ReputationRegistry":  "0x423a9904e39537a9997fbaF0f220d79D7d545763",
    "ValidationRegistry":  "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1",
    "AgentRegistry":       "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3",
}

# Try standard Etherscan API
ETHERSCAN_API = "https://api-sepolia.etherscan.io/api"

for name, address in contracts.items():
    params = {
        "module": "contract",
        "action": "getabi",
        "address": address,
        "apikey": ""  # Empty key should work for basic requests
    }
    
    resp = requests.get(ETHERSCAN_API, params=params)
    print(f"\n{name}: Status {resp.status_code}")
    print(f"Response text (first 500 chars): {resp.text[:500]}")
    
    try:
        data = resp.json()
        if data["status"] == "1":
            print(f"\n{'='*60}")
            print(f"CONTRACT: {name} ({address})")
            print(f"{'='*60}")
            abi_data = data["result"]
            print(abi_data)
            
            # Save to file
            filename = f"{name.lower()}_abi.json"
            with open(filename, "w") as f:
                f.write(abi_data)
            print(f"\n✅ Saved to {filename}")
        else:
            print(f"❌ {name}: {data['message']} — {data.get('result','')}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
