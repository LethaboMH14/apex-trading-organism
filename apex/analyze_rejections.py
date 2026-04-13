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

# Scan recent events
latest = w3.eth.block_number
from_block = max(0, latest - 50000)
print(f"Scanning blocks {from_block} to {latest} (latest: {latest})")

print("\n" + "=" * 80)
print("FETCHING EVENTS FOR AGENT ID 26")
print("=" * 80)

# Try all relevant event names
event_names = ["TradeRejected", "TradeApproved", "TradeIntentSubmitted"]

for event_name in event_names:
    try:
        event = getattr(contract.events, event_name)
        logs = event.get_logs(
            from_block=from_block,
            to_block='latest',
            argument_filters={"agentId": 26}
        )
        print(f"\n{event_name}: {len(logs)} events found")
        if logs:
            # Show last 5 events
            print(f"  Last {min(5, len(logs))} events:")
            for log in logs[-5:]:
                print(f"    Block {log['blockNumber']}: {dict(log['args'])}")
    except Exception as e:
        print(f"{event_name}: not found ({e})")

print("\n" + "=" * 80)
