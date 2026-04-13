import requests
import json

contracts = {
    "RiskRouter":          "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC",
    "ReputationRegistry":  "0x423a9904e39537a9997fbaF0f220d79D7d545763",
    "ValidationRegistry":  "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1",
    "AgentRegistry":       "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3",
}

# Try Sourcify API for verified contracts
SOURCIFY_API = "https://server.sourcify.dev"

for name, address in contracts.items():
    # Try both full and partial match
    for match_type in ["full_match", "partial_match"]:
        url = f"{SOURCIFY_API}/files/ethereum/sepolia/{address}/{match_type}"
        resp = requests.get(url)
        
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                print(f"\n{'='*60}")
                print(f"CONTRACT: {name} ({address})")
                print(f"Match type: {match_type}")
                print(f"{'='*60}")
                
                # Look for ABI file
                abi_found = False
                for file_info in data:
                    if file_info.get("name") == "abi.json":
                        abi_url = f"{SOURCIFY_API}/files/ethereum/sepolia/{address}/{match_type}/abi.json"
                        abi_resp = requests.get(abi_url)
                        if abi_resp.status_code == 200:
                            abi_data = abi_resp.text
                            print(abi_data)
                            
                            # Save to file
                            filename = f"{name.lower()}_abi.json"
                            with open(filename, "w") as f:
                                f.write(abi_data)
                            print(f"\n✅ Saved to {filename}")
                            abi_found = True
                            break
                
                if abi_found:
                    break
        else:
            print(f"{name} ({match_type}): Status {resp.status_code}")
