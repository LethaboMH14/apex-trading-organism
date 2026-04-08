from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia-rpc.publicnode.com'))
tx_hash = '0x6ac256a9966e5d0dd476b828265ff2dedba32063db21980ace92f481242d4f66'

print('Extracting Agent ID from transaction logs...')
receipt = w3.eth.get_transaction_receipt(tx_hash)

# Check each log for AgentRegistered event
for i, log in enumerate(receipt['logs']):
    print(f"\nLog {i}:")
    print(f"  Address: {log['address']}")
    print(f"  Topics: {len(log['topics'])} topics")
    
    # AgentRegistered event signature (first topic)
    if log['topics'] and len(log['topics']) >= 4:
        event_signature = log['topics'][0].hex()
        print(f"  Event signature: {event_signature}")
        
        # Check if this is AgentRegistered event
        if event_signature == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
            print("  ✅ Found AgentRegistered event!")
            
            # Extract agentId from topics[1] (second topic, first indexed parameter)
            agent_id_bytes = log['topics'][1]
            agent_id = int(agent_id_bytes.hex(), 16)
            print(f"  📋 Agent ID: {agent_id}")
            
            # Save to .env
            import os
            from dotenv import set_key
            env_file = 'c:\\Users\\USER\\Desktop\\APEX\\.env'
            set_key(env_file, 'APEX_AGENT_ID', str(agent_id))
            print(f"  💾 Updated .env: APEX_AGENT_ID={agent_id}")
            
            # Save to file
            import json
            from pathlib import Path
            Path('agent-id.json').write_text(json.dumps({'agentId': agent_id}, indent=2))
            print(f"  💾 Saved to agent-id.json")
            
            print(f"\n🎉 SUCCESS! Your APEX Agent ID is: {agent_id}")
            print(f"🔗 Transaction: https://sepolia.etherscan.io/tx/{tx_hash}")
            break
    else:
        print("  ❌ Not AgentRegistered event")

# If no AgentRegistered event found, check Etherscan
else:
    print(f"\n❌ No AgentRegistered event found in transaction logs")
    print(f"🔗 Check manually: https://sepolia.etherscan.io/tx/{tx_hash}")
    print("Look for 'AgentRegistered' event in the logs section")
