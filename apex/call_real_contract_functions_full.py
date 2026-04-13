from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("https://ethereum-sepolia-rpc.publicnode.com"))

contracts = {
    "RiskRouter":          "0xd6A6952545FF6E6E6681c2d15C59f9EB8F40FdBC",
    "ReputationRegistry":  "0x423a9904e39537a9997fbaF0f220d79D7d545763",
    "ValidationRegistry":  "0x92bF63E5C7Ac6980f237a7164Ab413BE226187F1",
    "AgentRegistry":       "0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3",
}

agent_id = 26

results = []

for contract_name, address in contracts.items():
    # Load ABI
    try:
        with open(f"{contract_name.lower()}_abi.json", "r") as f:
            abi = json.load(f)
    except FileNotFoundError:
        results.append(f"\n❌ {contract_name}: ABI file not found")
        continue
    
    # Create contract instance
    contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
    
    # Find all view functions that accept agentId as uint256
    view_functions = []
    for item in abi:
        if item.get("type") == "function" and item.get("stateMutability") == "view":
            inputs = item.get("inputs", [])
            if inputs and inputs[0].get("type") == "uint256":
                func_name = item.get("name")
                view_functions.append((func_name, inputs))
    
    results.append(f"\n{'='*80}")
    results.append(f"CONTRACT: {contract_name} ({address})")
    results.append(f"{'='*80}")
    results.append(f"\nFound {len(view_functions)} view functions with uint256 first parameter:")
    
    # Call each function with agentId=26
    for func_name, inputs in view_functions:
        input_str = ", ".join([f"{i['name']}({i['type']})" for i in inputs])
        results.append(f"\n  Function: {func_name}({input_str})")
        
        try:
            # Try with just agentId
            result = getattr(contract.functions, func_name)(agent_id).call()
            results.append(f"  ✅ Result: {result}")
        except Exception as e:
            # Try with None for additional params
            try:
                args = [agent_id] + [None] * (len(inputs) - 1)
                result = getattr(contract.functions, func_name)(*args).call()
                results.append(f"  ✅ Result: {result}")
            except Exception as e2:
                results.append(f"  ❌ Error: {str(e2)[:200]}")

# Print all results
print("\n".join(results))

# Save to file
with open("contract_function_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
print("\n\nSaved to contract_function_results.txt")
