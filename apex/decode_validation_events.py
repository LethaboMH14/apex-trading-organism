from web3 import Web3
from eth_abi import decode

rpc_url = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(rpc_url))

REGISTRY_ADDRESS = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"

# Event signature from logs: 0x5c19b748ded05e13d6fb5776172b6f813692e237572a5c725a43077cb82a67db
# This is keccak256("AttestationPosted(uint256,bytes32,uint8,uint8,string)")
# Topics: [signature, agentId, address, checkpointHash]
# Data: score, proofType, notes (string)

latest_block = w3.eth.block_number
from_block = max(0, latest_block - 10000)
print(f"Scanning blocks {from_block} to {latest_block}...")

logs = w3.eth.get_logs({
    "address": Web3.to_checksum_address(REGISTRY_ADDRESS),
    "fromBlock": from_block,
    "toBlock": latest_block
})

print(f"Total logs found: {len(logs)}")

# Filter for agentId=26 (0x1a in hex, but I saw 0x19=25, 0x1a=26 in topics)
agent26_logs = []
for log in logs:
    # Topics[1] is agentId (indexed)
    if len(log['topics']) >= 2:
        agentId = int(log['topics'][1].hex(), 16)
        if agentId == 26:
            agent26_logs.append(log)

print(f"\nLogs for agentId=26: {len(agent26_logs)}")

if agent26_logs:
    scores = []
    for log in agent26_logs:
        # Decode data: score (uint8), proofType (uint8), notes (string)
        # Data format: score (uint8), proofType (uint8), notes (string with offset and length)
        try:
            data = log['data']
            # First byte is score
            score = int(data[31:32].hex(), 16) if len(data) > 31 else 0
            # Second byte is proofType
            proofType = int(data[63:64].hex(), 16) if len(data) > 63 else 0
            scores.append(score)
        except Exception as e:
            print(f"Error decoding log: {e}")
    
    if scores:
        print(f"\nScore distribution for agentId=26:")
        print(f"  Total attestations: {len(scores)}")
        print(f"  Min score: {min(scores)}")
        print(f"  Max score: {max(scores)}")
        print(f"  Average score: {sum(scores)/len(scores):.2f}")
        print(f"  Scores below 100: {[s for s in scores if s < 100]}")
        print(f"  Count of scores < 100: {len([s for s in scores if s < 100])}")
        print(f"  Count of scores = 100: {len([s for s in scores if s == 100])}")
        
        # Show first 20 scores
        print(f"\n  First 20 scores: {scores[:20]}")
        print(f"  Last 20 scores: {scores[-20:]}")
else:
    print("No logs found for agentId=26 in last 10,000 blocks")
    print("\nChecking all agentIds in logs...")
    agentIds = set()
    for log in logs[:100]:  # Check first 100 logs
        if len(log['topics']) >= 2:
            agentId = int(log['topics'][1].hex(), 16)
            agentIds.add(agentId)
    print(f"AgentIds found: {sorted(list(agentIds))}")
