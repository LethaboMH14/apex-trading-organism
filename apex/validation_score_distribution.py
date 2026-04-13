import requests
import json
from web3 import Web3
from collections import Counter

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

print("=" * 80)
print("VALIDATION SCORE DISTRIBUTION ANALYSIS")
print("=" * 80)

attestations = contract.functions.getAttestations(26).call()
print(f"Total attestations: {len(attestations)}")

# Print first 3 raw attestations to see structure
print("\nFirst 3 raw attestations (to see tuple structure):")
for i, a in enumerate(attestations[:3]):
    print(f"attestation[{i}]: {a}")

# Extract scores — tuple structure may vary, try common positions
scores = []
for a in attestations:
    # Try index 3 (agentId, checkpointHash, validator, score, ...)
    try:
        score = a[3]
        scores.append(int(score))
    except:
        pass

if scores:
    print(f"\n" + "=" * 80)
    print("SCORE DISTRIBUTION")
    print("=" * 80)
    print(f"Min score: {min(scores)}")
    print(f"Max score: {max(scores)}")
    print(f"Sum: {sum(scores)}")
    print(f"Count: {len(scores)}")
    print(f"True average: {sum(scores)/len(scores):.4f}")
    
    # Distribution
    dist = Counter(scores)
    print("\nScore distribution:")
    for s in sorted(dist.keys()):
        print(f"  score {s}: {dist[s]} attestations ({dist[s]/len(scores)*100:.1f}%)")
    
    # Math: how many score=100 needed to reach avg=99?
    N = len(scores)
    S = sum(scores)
    target = 99
    # S + 100*K >= 99 * (N + K)
    # S + 100K >= 99N + 99K
    # K >= (99N - S) / (100 - 99)
    # K >= (99N - S)
    K = max(0, (target * N - S))
    print(f"\n" + "=" * 80)
    print("PATH TO AVERAGE SCORE 99")
    print("=" * 80)
    print(f"Current: {sum(scores)/len(scores):.4f}")
    print(f"Target: 99.0000")
    print(f"Need {K} more score=100 attestations")
    print(f"  At 1/minute: {K/60:.1f} hours")
    print(f"  At 1/30sec:  {K/120:.1f} hours")
    
    # Also calculate for avg=100
    target100 = 100
    K100 = max(0, (target100 * N - S))
    print(f"\nPATH TO AVERAGE SCORE 100")
    print("=" * 80)
    print(f"Need {K100} more score=100 attestations")
    print(f"  At 1/minute: {K100/60:.1f} hours")
    print(f"  At 1/30sec:  {K100/120:.1f} hours")

print("\n" + "=" * 80)
