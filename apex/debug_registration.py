"""
Debug script to diagnose APEX registration failure.
Run: python apex/debug_registration.py
"""
import os
import sys
sys.path.insert(0, 'apex')

from dotenv import load_dotenv
load_dotenv()

from web3 import Web3
from eth_account import Account

SEPOLIA_RPC = os.getenv("SEPOLIA_RPC_URL", "https://ethereum-sepolia-rpc.publicnode.com")
AGENT_REGISTRY = "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3"

operator_key = os.getenv("APEX_OPERATOR_PRIVATE_KEY") or os.getenv("APEX_PRIVATE_KEY", "")
agent_key    = os.getenv("APEX_AGENT_WALLET_PRIVATE_KEY") or operator_key

print("=" * 60)
print("APEX REGISTRATION DIAGNOSTICS")
print("=" * 60)

# 1. Check keys
print(f"\n1. PRIVATE KEYS")
print(f"   Operator key set: {'✅' if operator_key else '❌ MISSING'}")
print(f"   Agent key set:    {'✅' if agent_key else '❌ MISSING'}")

if not operator_key:
    print("\n❌ APEX_PRIVATE_KEY or APEX_OPERATOR_PRIVATE_KEY not set in .env")
    sys.exit(1)

operator = Account.from_key(operator_key)
agent     = Account.from_key(agent_key)
print(f"   Operator address: {operator.address}")
print(f"   Agent address:    {agent.address}")

# 2. Check connection
print(f"\n2. NETWORK CONNECTION")
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))
connected = w3.is_connected()
print(f"   Connected to Sepolia: {'✅' if connected else '❌ FAILED'}")
print(f"   RPC URL: {SEPOLIA_RPC}")

if not connected:
    print("\n❌ Cannot connect to Sepolia RPC. Try a different RPC:")
    print("   SEPOLIA_RPC_URL=https://rpc.sepolia.org")
    sys.exit(1)

chain_id = w3.eth.chain_id
print(f"   Chain ID: {chain_id} {'✅ Sepolia' if chain_id == 11155111 else '❌ WRONG NETWORK'}")

# 3. Check balance
print(f"\n3. WALLET BALANCE")
balance_wei = w3.eth.get_balance(operator.address)
balance_eth = float(w3.from_wei(balance_wei, 'ether'))
print(f"   Operator balance: {balance_eth:.6f} ETH")
if balance_eth < 0.001:
    print("   ❌ INSUFFICIENT ETH — need at least 0.001 ETH for gas")
    print("   Get Sepolia ETH from: https://faucet.quicknode.com/ethereum/sepolia")
else:
    print(f"   ✅ Sufficient for gas")

# 4. Check gas price
print(f"\n4. GAS PRICE")
gas_price = w3.eth.gas_price
print(f"   Current gas price: {w3.from_wei(gas_price, 'gwei'):.2f} gwei")
estimated_cost = (500000 * gas_price)
print(f"   Estimated tx cost: {float(w3.from_wei(estimated_cost, 'ether')):.6f} ETH")

# 5. Try to simulate the registration call
print(f"\n5. CONTRACT CALL SIMULATION")
AGENT_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "agentWallet",  "type": "address"},
            {"name": "name",         "type": "string"},
            {"name": "description",  "type": "string"},
            {"name": "capabilities", "type": "string[]"},
            {"name": "agentURI",     "type": "string"}
        ],
        "name": "register",
        "outputs": [{"name": "agentId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

try:
    registry = w3.eth.contract(
        address=Web3.to_checksum_address(AGENT_REGISTRY),
        abi=AGENT_REGISTRY_ABI
    )
    # Try eth_call to simulate
    result = registry.functions.register(
        agent.address,
        "APEX Trading Organism",
        "Self-evolving multi-agent AI trading system",
        ["trading", "eip712-signing"],
        "https://github.com/apex"
    ).call({"from": operator.address})
    print(f"   ✅ Call simulation succeeded! agentId would be: {result}")
except Exception as e:
    print(f"   ❌ Call simulation failed: {e}")
    print(f"   This is the root cause of the registration failure")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)
