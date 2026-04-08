import sys, os
sys.path.insert(0, 'apex')
from dotenv import load_dotenv
load_dotenv()
from web3 import Web3
from eth_account import Account

operator_key = os.getenv('APEX_OPERATOR_PRIVATE_KEY') or os.getenv('APEX_PRIVATE_KEY')
agent_key = os.getenv('APEX_AGENT_WALLET_PRIVATE_KEY') or operator_key
operator = Account.from_key(operator_key)
agent = Account.from_key(agent_key)

w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia-rpc.publicnode.com'))

ABI = [{
    'inputs': [
        {'name': 'agentWallet',  'type': 'address'},
        {'name': 'name',         'type': 'string'},
        {'name': 'description',  'type': 'string'},
        {'name': 'capabilities', 'type': 'string[]'},
        {'name': 'agentURI',     'type': 'string'}
    ],
    'name': 'register',
    'outputs': [{'name': 'agentId', 'type': 'uint256'}],
    'stateMutability': 'nonpayable',
    'type': 'function'
},
{
    'anonymous': False,
    'inputs': [
        {'indexed': True,  'name': 'agentId',       'type': 'uint256'},
        {'indexed': True,  'name': 'operatorWallet', 'type': 'address'},
        {'indexed': False, 'name': 'agentWallet',    'type': 'address'},
        {'indexed': False, 'name': 'name',           'type': 'string'}
    ],
    'name': 'AgentRegistered',
    'type': 'event'
}]

registry = w3.eth.contract(
    address=Web3.to_checksum_address('0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3'),
    abi=ABI
)

nonce = w3.eth.get_transaction_count(operator.address)
tx = registry.functions.register(
    agent.address,
    'APEX Trading Organism',
    'Self-evolving multi-agent AI trading system with ERC-8004 on-chain proofs',
    ['trading', 'eip712-signing', 'autonomous-learning', 'multi-agent'],
    'https://github.com/apex'
).build_transaction({
    'from': operator.address,
    'nonce': nonce,
    'gas': 1000000,
    'gasPrice': w3.eth.gas_price,
})

signed = w3.eth.account.sign_transaction(tx, private_key=operator_key)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f'TX sent: {tx_hash.hex()}')
print(f'Waiting for confirmation...')
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
status = 'SUCCESS' if receipt['status'] == 1 else 'FAILED'
print(f'Status: {status}')
print(f'Block: {receipt["blockNumber"]}')
print(f'Gas used: {receipt["gasUsed"]}')
print(f'Explorer: https://sepolia.etherscan.io/tx/{tx_hash.hex()}')

if receipt['status'] == 1:
    try:
        events = registry.events.AgentRegistered().process_receipt(receipt)
        agent_id = events[0]['args']['agentId']
        print(f'Agent ID: {agent_id}')
        import json
        from pathlib import Path
        Path('agent-id.json').write_text(json.dumps({'agentId': agent_id}))
        print(f'Saved to agent-id.json')
        print(f'Add to .env: APEX_AGENT_ID={agent_id}')
    except Exception as e:
        print(f'Could not parse agentId from events: {e}')
        print('Check the explorer link above for your agentId')
