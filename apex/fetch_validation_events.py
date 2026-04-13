from web3 import Web3

rpc_url = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(rpc_url))

REGISTRY_ADDRESS = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"

# Try different event names
event_names = ["AttestationPosted", "ValidationPosted", "CheckpointPosted", "ScorePosted"]

for event_name in event_names:
    try:
        abi = [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "agentId", "type": "uint256"},
                    {"indexed": False, "name": "checkpointHash", "type": "bytes32"},
                    {"indexed": False, "name": "score", "type": "uint8"},
                    {"indexed": False, "name": "proofType", "type": "uint8"},
                    {"indexed": False, "name": "notes", "type": "string"}
                ],
                "name": event_name,
                "type": "event"
            }
        ]
        
        contract = w3.eth.contract(address=Web3.to_checksum_address(REGISTRY_ADDRESS), abi=abi)
        
        # Try to get events
        events = contract.events[event_name].get_logs(
            fromBlock=0,
            toBlock='latest',
            argument_filters={"agentId": 26}
        )
        
        print(f"✓ Event '{event_name}' found: {len(events)} events")
        if events:
            scores = [e['args']['score'] for e in events]
            print(f"  Score distribution: min={min(scores)}, max={max(scores)}, avg={sum(scores)/len(scores):.2f}")
            print(f"  Scores below 100: {[s for s in scores if s < 100]}")
            print(f"  First 5 scores: {scores[:5]}")
            print(f"  Last 5 scores: {scores[-5:]}")
    except Exception as e:
        print(f"✗ Event '{event_name}' failed: {str(e)[:100]}")

print("\n--- Trying full ABI from apex_identity.py ---")

# Try with the full ABI from apex_identity.py
FULL_ABI = [
    {
        "inputs": [
            {"name": "agentId", "type": "uint256"},
            {"name": "checkpointHash", "type": "bytes32"},
            {"name": "score", "type": "uint8"},
            {"name": "proofType", "type": "uint8"},
            {"name": "proof", "type": "bytes"},
            {"name": "notes", "type": "string"}
        ],
        "name": "postAttestation",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=Web3.to_checksum_address(REGISTRY_ADDRESS), abi=FULL_ABI)

# Get all logs from the contract address
print("Fetching all logs from contract address...")
try:
    # Get recent block number
    latest_block = w3.eth.block_number
    print(f"Latest block: {latest_block}")
    
    # Scan last 10000 blocks for efficiency
    from_block = max(0, latest_block - 10000)
    print(f"Scanning blocks {from_block} to {latest_block}...")
    
    logs = w3.eth.get_logs({
        "address": Web3.to_checksum_address(REGISTRY_ADDRESS),
        "fromBlock": from_block,
        "toBlock": latest_block
    })
    
    print(f"Total logs found: {len(logs)}")
    
    # Try to decode logs
    for i, log in enumerate(logs[:10]):  # Show first 10
        print(f"\nLog {i+1}:")
        print(f"  Block: {log['blockNumber']}")
        print(f"  Tx hash: {log['transactionHash'].hex()}")
        print(f"  Topics: {log['topics']}")
        print(f"  Data: {log['data']}")
        
except Exception as e:
    print(f"Error fetching logs: {e}")
