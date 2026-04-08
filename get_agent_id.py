from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia-rpc.publicnode.com'))
tx_hash = '0x6ac256a9966e5d0dd476b828265ff2dedba32063db21980ace92f481242d4f66'

print('Getting transaction receipt...')
receipt = w3.eth.get_transaction_receipt(tx_hash)

print(f"Transaction status: {'SUCCESS' if receipt['status'] == 1 else 'FAILED'}")
print(f"Block: {receipt['blockNumber']}")
print(f"Gas used: {receipt['gasUsed']}")

# Print all logs to debug
print(f"\nNumber of logs: {len(receipt['logs'])}")
for i, log in enumerate(receipt['logs']):
    print(f"Log {i}:")
    print(f"  Address: {log['address']}")
    print(f"  Topics: {log['topics']}")
    print(f"  Data: {log['data']}")

# Try to get agent ID directly from the contract
try:
    # Simple ABI to just get the agent ID from the event
    registry = w3.eth.contract(
        address='0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3',
        abi=[{
            'anonymous': False,
            'inputs': [
                {'indexed': True,  'name': 'agentId', 'type': 'uint256'},
                {'indexed': True,  'name': 'operatorWallet', 'type': 'address'},
                {'indexed': True,  'name': 'agentWallet', 'type': 'address'},
                {'indexed': False, 'name': 'name', 'type': 'string'}
            ],
            'name': 'AgentRegistered',
            'type': 'event'
        }]
    )
    
    # Process logs manually
    for log in receipt['logs']:
        if log['address'].lower() == '0x97b07ddc405b0c28b17559affe63bdb3632d0ca3'.lower():
            # The agentId is in topics[1] (indexed parameter)
            agent_id_bytes = log['topics'][1]
            agent_id = int(agent_id_bytes.hex(), 16)
            print(f"\n✅ Found Agent ID: {agent_id}")
            print(f"Add to .env: APEX_AGENT_ID={agent_id}")
            
            # Save to file
            import json
            from pathlib import Path
            Path('agent-id.json').write_text(json.dumps({'agentId': agent_id}))
            print("Saved to agent-id.json")
            break
            
except Exception as e:
    print(f"Error parsing logs: {e}")
    print("Check the transaction on Etherscan to find your Agent ID")
    print("https://sepolia.etherscan.io/tx/0x6ac256a9966e5d0dd476b828265ff2dedba32063db21980ace92f481242d4f66")
