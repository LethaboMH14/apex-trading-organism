import requests
import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://ethereum-sepolia-rpc.publicnode.com"))

# Capture all output to file
full_output = []

def log_print(text):
    print(text)
    full_output.append(text)

log_print("=" * 80)
log_print("STEP 2: ReputationRegistry - All view functions for agentId=26")
log_print("=" * 80)

resp = requests.get("https://eth-sepolia.blockscout.com/api", params={
    "module": "contract", "action": "getabi",
    "address": "0x423a9904e39537a9997fbaF0f220d79D7d545763",
})
abi = json.loads(resp.json()["result"])

contract = w3.eth.contract(
    address=Web3.to_checksum_address("0x423a9904e39537a9997fbaF0f220d79D7d545763"),
    abi=abi
)

log_print("ReputationRegistry functions:")
for item in abi:
    if item.get("type") == "function":
        inputs = [(i["name"], i["type"]) for i in item.get("inputs", [])]
        outputs = [o["type"] for o in item.get("outputs", [])]
        mutability = item.get("stateMutability", "nonpayable")
        log_print(f"  {item['name']}({inputs}) → {outputs} [{mutability}]")

log_print("\nCalling all view functions with agentId=26:")
for item in abi:
    if item.get("type") == "function" and item.get("stateMutability") == "view":
        inputs = item.get("inputs", [])
        if len(inputs) == 1 and inputs[0]["type"] == "uint256":
            try:
                fn = getattr(contract.functions, item["name"])
                result = fn(26).call()
                log_print(f"  {item['name']}(26) = {result}")
            except Exception as e:
                log_print(f"  {item['name']}(26) = ERROR: {str(e)[:100]}")

log_print("\n" + "=" * 80)
log_print("STEP 3: ValidationRegistry - All view functions for agentId=26")
log_print("=" * 80)

resp2 = requests.get("https://eth-sepolia.blockscout.com/api", params={
    "module": "contract", "action": "getabi",
    "address": "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1",
})
abi2 = json.loads(resp2.json()["result"])
contract2 = w3.eth.contract(
    address=Web3.to_checksum_address("0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"),
    abi=abi2
)

log_print("ValidationRegistry functions:")
for item in abi2:
    if item.get("type") == "function":
        inputs = [(i["name"], i["type"]) for i in item.get("inputs", [])]
        outputs = [o["type"] for o in item.get("outputs", [])]
        mutability = item.get("stateMutability", "nonpayable")
        log_print(f"  {item['name']}({inputs}) → {outputs} [{mutability}]")

log_print("\nCalling all view functions with agentId=26:")
for item in abi2:
    if item.get("type") == "function" and item.get("stateMutability") == "view":
        inputs = item.get("inputs", [])
        if len(inputs) == 1 and inputs[0]["type"] == "uint256":
            try:
                fn = getattr(contract2.functions, item["name"])
                result = fn(26).call()
                log_print(f"  {item['name']}(26) = {result}")
            except Exception as e:
                log_print(f"  {item['name']}(26) = ERROR: {str(e)[:100]}")

log_print("\n" + "=" * 80)
log_print("STEP 4: AgentRegistry - All view functions for agentId=26")
log_print("=" * 80)

resp3 = requests.get("https://eth-sepolia.blockscout.com/api", params={
    "module": "contract", "action": "getabi",
    "address": "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3",
})
abi3 = json.loads(resp3.json()["result"])
contract3 = w3.eth.contract(
    address=Web3.to_checksum_address("0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"),
    abi=abi3
)

log_print("AgentRegistry functions:")
for item in abi3:
    if item.get("type") == "function":
        inputs = [(i["name"], i["type"]) for i in item.get("inputs", [])]
        outputs = [o["type"] for o in item.get("outputs", [])]
        mutability = item.get("stateMutability", "nonpayable")
        log_print(f"  {item['name']}({inputs}) → {outputs} [{mutability}]")

log_print("\nCalling all view functions with agentId=26:")
for item in abi3:
    if item.get("type") == "function" and item.get("stateMutability") == "view":
        inputs = item.get("inputs", [])
        if len(inputs) == 1 and inputs[0]["type"] == "uint256":
            try:
                fn = getattr(contract3.functions, item["name"])
                result = fn(26).call()
                log_print(f"  {item['name']}(26) = {result}")
            except Exception as e:
                log_print(f"  {item['name']}(26) = ERROR: {str(e)[:100]}")

log_print("\n" + "=" * 80)

# Save to file
with open("contract_scoring_analysis.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(full_output))
log_print("\n✅ Saved to contract_scoring_analysis.txt")
