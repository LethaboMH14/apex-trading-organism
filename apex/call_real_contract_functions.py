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

print("=" * 80)
print(f"CALLING ALL VIEW FUNCTIONS FOR AGENT ID {agent_id}")
print("=" * 80)

for contract_name, address in contracts.items():
    print(f"\n{'='*80}")
    print(f"CONTRACT: {contract_name} ({address})")
    print(f"{'='*80}")
    
    # Load ABI
    try:
        with open(f"{contract_name.lower()}_abi.json", "r") as f:
            abi = json.load(f)
    except FileNotFoundError:
        print(f"❌ ABI file not found for {contract_name}")
        continue
    
    # Create contract instance
    contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
    
    # Find all view functions that accept agentId as uint256
    view_functions = []
    for item in abi:
        if item.get("type") == "function" and item.get("stateMutability") == "view":
            inputs = item.get("inputs", [])
            # Check if first input is uint256 named something like agentId
            if inputs and inputs[0].get("type") == "uint256":
                func_name = item.get("name")
                view_functions.append((func_name, inputs))
    
    print(f"\nFound {len(view_functions)} view functions with uint256 first parameter:")
    for func_name, inputs in view_functions:
        input_str = ", ".join([f"{i['name']}({i['type']})" for i in inputs])
        print(f"  - {func_name}({input_str})")
    
    # Call each function with agentId=26
    print(f"\nCalling functions with agentId={agent_id}:")
    for func_name, inputs in view_functions:
        try:
            # Build arguments - just pass agentId for first param, try None for others
            args = [agent_id] + [None] * (len(inputs) - 1)
            result = getattr(contract.functions, func_name)(*args).call()
            print(f"  ✅ {func_name}: {result}")
        except Exception as e:
            # Try with just agentId if there are optional params
            try:
                result = getattr(contract.functions, func_name)(agent_id).call()
                print(f"  ✅ {func_name}: {result}")
            except Exception as e2:
                print(f"  ❌ {func_name}: {str(e2)[:100]}")

print("\n" + "=" * 80)
print("COMPLETE")
print("=" * 80)
