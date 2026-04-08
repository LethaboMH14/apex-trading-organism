import time
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://ethereum-sepolia-rpc.publicnode.com'))
tx_hash = '0x6ac256a9966e5d0dd476b828265ff2dedba32063db21980ace92f481242d4f66'

print('Checking transaction status...')
print(f'Explorer: https://sepolia.etherscan.io/tx/{tx_hash}')

# Wait and check multiple times
for i in range(10):
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if receipt:
                status = 'SUCCESS' if receipt['status'] == 1 else 'FAILED'
                print(f'Status: {status}')
                print(f'Block: {receipt["blockNumber"]}')
                print(f'Gas used: {receipt["gasUsed"]}')
                
                if receipt['status'] == 1:
                        # Try to parse agent ID from events
                        try:
                                ABI = [{
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
                                        address='0x97b07dDc405B0c28B17559aFFE63BdB3632d0ca3',
                                        abi=ABI
                                )
                                events = registry.events.AgentRegistered().process_receipt(receipt)
                                agent_id = events[0]['args']['agentId']
                                print(f'Agent ID: {agent_id}')
                                print(f'Add to .env: APEX_AGENT_ID={agent_id}')
                        except Exception as e:
                                print(f'Could not parse agentId: {e}')
                break
        else:
                print(f'Attempt {i+1}: Transaction not yet mined...')
                time.sleep(15)
    except Exception as e:
        print(f'Attempt {i+1}: {e}')
        time.sleep(15)
