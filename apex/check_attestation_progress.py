from web3 import Web3
import requests
import json

w3 = Web3(Web3.HTTPProvider("https://ethereum-sepolia-rpc.publicnode.com"))

resp = requests.get("https://eth-sepolia.blockscout.com/api", params={
    "module": "contract", "action": "getabi",
    "address": "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1",
})
abi = json.loads(resp.json()["result"])
contract = w3.eth.contract(
    address=Web3.to_checksum_address("0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"),
    abi=abi
)

count = contract.functions.attestationCount(26).call()
avg = contract.functions.getAverageValidationScore(26).call()

print("=" * 80)
print("ATTESTATION PROGRESS CHECK")
print("=" * 80)
print(f"Attestations: {count} (was 1,096)")
print(f"Average score: {avg} (was 98.54)")
print(f"New attestations this session: {count - 1096}")

# Calculate hourly rate
new_attestations = count - 1096
if new_attestations > 0:
    print(f"\nHourly rate: {new_attestations} attestations/hour")
    if new_attestations >= 60:
        print("✅ On track (>= 60/hour)")
    else:
        print(f"⚠️  Below target (need >= 60/hour)")
else:
    print("\n⚠️  No new attestations - agent may not be posting!")

print("=" * 80)
