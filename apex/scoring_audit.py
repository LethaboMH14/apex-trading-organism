from web3 import Web3
import os

w3 = Web3(Web3.HTTPProvider(
    os.getenv("SEPOLIA_RPC_URL", "https://ethereum-sepolia-rpc.publicnode.com")
))

print("=" * 60)
print("SCORING AUDIT FOR AGENT ID 26")
print("=" * 60)

# STEP 1: Check vault claim status
print("\n--- STEP 1: VAULT CLAIM STATUS ---")
VAULT_ADDRESS = "0x0E7CD8ef9743FEcf94f9103033a044caBD45fC90"
VAULT_ABI = [
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "hasClaimed",
        "outputs": [{"type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getBalance",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

vault = w3.eth.contract(
    address=Web3.to_checksum_address(VAULT_ADDRESS), abi=VAULT_ABI
)
claimed = vault.functions.hasClaimed(26).call()
balance = vault.functions.getBalance(26).call()
print(f"Vault claimed: {claimed}")
print(f"Vault balance: {w3.from_wei(balance, 'ether')} ETH")

# STEP 2: Check approved trades count on RiskRouter
print("\n--- STEP 2: RISK ROUTER TRADE COUNT ---")
RISK_ROUTER_ADDRESS = "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC"
RISK_ROUTER_ABI = [
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getApprovedTradeCount",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getIntentNonce",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

router = w3.eth.contract(
    address=Web3.to_checksum_address(RISK_ROUTER_ADDRESS), abi=RISK_ROUTER_ABI
)

# Try getApprovedTradeCount
try:
    approved = router.functions.getApprovedTradeCount(26).call()
    print(f"Approved trades: {approved}")
except Exception as e:
    print(f"getApprovedTradeCount failed: {e}")

nonce = router.functions.getIntentNonce(26).call()
print(f"Total intents submitted (nonce): {nonce}")

# STEP 3: Check reputation registry
print("\n--- STEP 3: REPUTATION REGISTRY ---")
REPUTATION_REGISTRY_ADDRESS = "0x423a9904e39537a9997fbaF0f220d79D7d545763"
REP_ABI = [
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getClients",
        "outputs": [{"type": "address[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "agentId", "type": "uint256"},
            {"name": "clientAddresses", "type": "address[]"},
            {"name": "tag1", "type": "string"},
            {"name": "tag2", "type": "string"}
        ],
        "name": "getSummary",
        "outputs": [
            {"name": "count",               "type": "uint64"},
            {"name": "summaryValue",        "type": "int128"},
            {"name": "summaryValueDecimals","type": "uint8"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

rep = w3.eth.contract(
    address=Web3.to_checksum_address(REPUTATION_REGISTRY_ADDRESS), abi=REP_ABI
)
try:
    clients = rep.functions.getClients(26).call()
    print(f"Reputation clients: {len(clients)} — {clients}")
except Exception as e:
    print(f"getClients failed: {e}")

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)
