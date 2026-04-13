from web3 import Web3
import os

# Use Sepolia RPC from .env.example
rpc_url = "https://ethereum-sepolia-rpc.publicnode.com"
w3 = Web3(Web3.HTTPProvider(rpc_url))

REGISTRY_ADDRESS = "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1"
ABI = [
    {
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "name": "getAverageValidationScore",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

contract = w3.eth.contract(address=Web3.to_checksum_address(REGISTRY_ADDRESS), abi=ABI)
avg = contract.functions.getAverageValidationScore(26).call()
print(f"Current on-chain average: {avg}")
